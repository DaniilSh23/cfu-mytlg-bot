import asyncio
import json
import random

from openai.error import RateLimitError
from pyrogram import Client, filters

from filters.client_filters import listening_channel_filter
from settings.config import MY_LOGGER, CLIENT_CHANNELS, TOKEN, PAUSE_BETWEEN_JOIN_TO_CHANNELS, \
    PAUSE_BETWEEN_FIVE_CHANNELS
from utils.post_filters import PostFilters
from utils.req_to_bot_api import get_related_news, write_new_post, send_subscription_results, update_channels
from utils.work_with_clients import check_channel_async


@Client.on_message(filters.channel & listening_channel_filter)
async def listening_chat_handler(client, update):
    """
    Ловим апдейты от чатов, которые прослушиваем.
    """
    MY_LOGGER.info(f'Аккаунт PK=={client.acc_pk!r} | Получен апдейт из прослушиваемого канала с ID == {update.chat.id}')

    MY_LOGGER.debug(f'Ищем нужный канал в общем списке')
    channels = CLIENT_CHANNELS[client.acc_pk]
    this_channel = list(filter(lambda ch: str(ch.get('channel_id')) == str(update.chat.id), channels))[0]
    MY_LOGGER.debug(f'Инфа об этом канале: {this_channel}')

    MY_LOGGER.debug(f'Получаем все новостные посты для темы данного канала')
    related_news = await get_related_news(ch_pk=this_channel.get('pk'))

    if related_news is None:
        MY_LOGGER.warning(f'Новостной пост из канала PK=={this_channel.get("pk")} не был обработан.')
        return

    # Проверка на наличие в постах эмбеддингов
    posts_lst = []
    for i_post in related_news:
        if i_post.get('embedding'):
            posts_lst.append(i_post)

    if len(posts_lst) > 0:
        MY_LOGGER.debug(f'Вызываем фильтры')
        try:
            post_filters_obj = PostFilters(
                new_post=update.text,
                old_posts=[(i_post.get("text"), i_post.get("embedding").split()) for i_post in posts_lst],
            )
            filtration_rslt = await post_filters_obj.complete_filtering()
        except RateLimitError as err:
            MY_LOGGER.warning(f'Проблема с запросами к OpenAI, откидываем пост. Ошибка: {err.error}')
            return
        except Exception as err:
            MY_LOGGER.error(f'Необрабатываемая проблема на этапе фильтрации поста и запросов к OpenAI. '
                            f'Пост будет отброшен. Ошибка: {err} | Текст поста: {update.text!r}')
            return
        if all(filtration_rslt):
            MY_LOGGER.debug(f'Пост прошёл фильтры, отправляем его в БД.')
            await write_new_post(
                ch_pk=this_channel.get("pk"),
                text=update.text,
                # Тут через map преобразуем float в str и соединяем это всё дело через пробел
                embedding=' '.join(list(map(lambda numb: str(numb), post_filters_obj.new_post_embedding)))
            )
        else:
            MY_LOGGER.debug(f'Фильтры для поста не пройдены. Откидываем пост.')
    else:
        MY_LOGGER.debug(f'Нет постов для сравнения, сходимся на том, что новый пост уникален.')
        new_post_embedding = await PostFilters.make_embedding(text=update.text)
        await write_new_post(
            ch_pk=this_channel.get("pk"),
            text=update.text,
            # Тут через map преобразуем float в str и соединяем это всё дело через пробел
            embedding=' '.join(list(map(lambda numb: str(numb), new_post_embedding)))
        )


@Client.on_message(filters.bot & filters.command('subscribe_to_channels') & filters.document)
async def subscribe_to_channels(client, update):    # TODO: эта дрочь переписана, но не проверена
    """
    Хэндлер на команду от бота начать подписываться на каналы.
    """
    MY_LOGGER.info(f'Получен апдейт с командой от бота subscribe_to_channels на аккаунт с PK=={client.acc_pk!r}')

    MY_LOGGER.debug(f'Скачиваем файл с данными для задачи в память и преобразуем в словарь')
    file = await update.download(in_memory=True)
    file_data = file.getvalue().decode('utf-8')
    cmd_data_dct = json.loads(file_data)

    # Словарь с результатами подписки
    task_result_dct = dict(token=TOKEN, task_pk=cmd_data_dct.get("task_pk"), results=[])    # TODO: эту херню скорее всего надо будет убрать из кода
    total_ch = len(cmd_data_dct["data"])
    ch_numb = 0
    actions_story = ''
    success_subs = 0
    fail_subs = 0
    complete_channels = {
        "token": TOKEN,
        "acc_pk": int(client.acc_pk),
        "channels": [],
    }

    for i_ch_pk, i_ch_lnk in cmd_data_dct["data"]:
        ch_numb += 1
        MY_LOGGER.debug(f'Подписываемся на {ch_numb} канал из {total_ch}')
        check_ch_rslt = await check_channel_async(app=client, channel_link=i_ch_lnk)

        # Подписка не удалась
        if not check_ch_rslt.get('success'):
            fail_subs += 1
            actions_story = f'{check_ch_rslt.get("action_story")}\n{actions_story}'
            task_result_dct.get('results').append({
                'ch_pk': i_ch_pk,
                'success': check_ch_rslt.get('success'),
                'description': check_ch_rslt.get('result').get('description'),
            })
            if check_ch_rslt.get('break_ch'):
                MY_LOGGER.warning(f'Останавливаем подписку на каналы аккаунтом PK == {client.acc_pk!r}')
                break
            continue

        # Успешная подписка
        success_subs += 1
        actions_story = f'{check_ch_rslt.get("action_story")}\n{actions_story}'
        i_ch_dct = {
            'ch_pk': i_ch_pk,
            'success': check_ch_rslt.get('success'),
            'ch_id': check_ch_rslt.get('result').get('ch_id'),
            'ch_name': check_ch_rslt.get('result').get('ch_name'),
            'ch_lnk': i_ch_lnk,
            'description': check_ch_rslt.get('result').get('description'),
            'subscribers_numb': check_ch_rslt.get('result').get('members_count')
        }
        task_result_dct.get('results').append(i_ch_dct)
        complete_channels['channels'].append(i_ch_dct)

        # Пауза перед следующей подпиской
        if ch_numb % 5 == 0 and ch_numb < total_ch:
            sleep_time = random.randint(*PAUSE_BETWEEN_FIVE_CHANNELS)
            MY_LOGGER.debug(f'Аккаунт PK == {client.acc_pk!r} | '
                            f'Отправляем запрос на запись каналов, на которые уже подписались.')

            # complete_channels = {     # TODO: потом убрать, как будет ясно, что всё ок
            #     "token": TOKEN,
            #     "acc_pk": int(client.acc_pk),
            #     "channels": [i_ch for i_ch in task_result_dct.get('results')[ch_numb - 5:] if i_ch.get("success")],
            # }

            ch_update_rslt = await update_channels(req_data=complete_channels)
            if not ch_update_rslt:
                MY_LOGGER.warning(f'Аккаунт PK == {client.acc_pk!r} | Не удался запрос для записи каналов')
            complete_channels['channels'] = []

            # Отправляем счётчики подписок, историю действий и очищаем эти переменные
            rslt = await send_subscription_results(
                task_pk=int(cmd_data_dct.get("task_pk")),
                actions_story=actions_story,
                success_subs=success_subs,
                fail_subs=fail_subs,
            )
            if not rslt:
                MY_LOGGER.warning(f'Аккаунт PK == {client.acc_pk!r} | '
                                  f'Не удался запрос для записи счетчиков и истории подписок. '
                                  f'Их значения до очистки:\n\tactions_story == {actions_story!r}'
                                  f'\n\tsuccess_subs == {success_subs!r}\n\tfail_subs == {fail_subs!r}')
            actions_story = ''
            success_subs = 0
            fail_subs = 0

        else:
            sleep_time = random.randint(*PAUSE_BETWEEN_JOIN_TO_CHANNELS)

        if ch_numb < total_ch:  # Проверка, чтобы не ждать после крайней подписки
            MY_LOGGER.debug(f'Аккаунт PK == {client.acc_pk!r} | Пауза перед следующей подпиской {sleep_time} сек.')
            await asyncio.sleep(sleep_time)
            MY_LOGGER.debug(f'Аккаунт PK == {client.acc_pk!r} | '
                            f'Город засыпает, просыпается аккаунт для дальнейших подписок на каналы.')

    # Блок ниже выполняется по окончании итерации по каналам
    MY_LOGGER.debug(f'Отправляем в БД результаты подписки аккаунтом PK == {client.acc_pk!r} с флагом завершения!')
    send_rslt = await send_subscription_results(
                task_pk=int(cmd_data_dct.get("task_pk")),
                actions_story=actions_story,
                success_subs=success_subs,
                fail_subs=fail_subs,
                status='success',
                end_flag=True,
            )

    if send_rslt:
        MY_LOGGER.debug(f'Пополняем список каналов для аккаунта PK == {client.acc_pk!r}')
        for i_ch in task_result_dct.get('results'):
            if i_ch.get('success'):
                CLIENT_CHANNELS[client.acc_pk].append({
                    "pk": i_ch.get('ch_pk'),
                    "channel_id": i_ch.get('ch_id'),
                    "channel_name": i_ch.get('ch_name'),
                    "channel_link": i_ch.get('ch_lnk'),
                })

    ch_update_rslt = await update_channels(req_data=complete_channels)
    if not ch_update_rslt:
        MY_LOGGER.warning(f'Аккаунт PK == {client.acc_pk!r} | Не удался запрос для записи каналов')

    await update.delete()  # удаляем сообщение с командой


# @Client.on_message()
async def all_updates(client, update):
    """
    Все апдейты
    """
    MY_LOGGER.success(f'Клиент {client.name!r} в работе. Получил апдейт.')
    MY_LOGGER.debug(update)
