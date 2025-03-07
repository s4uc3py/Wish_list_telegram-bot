# Wishlist Bot 🎁

Телеграм-бот для управления списком подарков с возможностью бронирования. Идеально подходит для организации мероприятий, где гости могут выбирать и резервировать подарки.

## Особенности ✨

- 📃 Просмотр списка подарков с деталями
- 🔒 Бронирование/отмена бронирования подарков
- 👨💻 Админ-панель для управления контентом
- 📊 Просмотр статистики бронирований
- 📝 Логирование всех действий
- 🔄 Автосохранение данных в JSON-файл

## Установка ⚙️

### Локальная установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/s4uc3py/Wish_list_telegram-bot.git
```
2. Создайте бота через @BotFather и получите токен

3. В файле wishlist-bot.py замените 'YOUR_BOT_TOKEN' на ваш токен

4. Установите зависимости:
```bash
pip install .
```

5. Запустите бота:
```bash
python wishlist-bot.py
```

### Установка с использованием Docker

1. Клонируйте репозиторий:
```bash
git clone https://github.com/s4uc3py/Wish_list_telegram-bot.git
```
2. Перейдите в директорию проекта:
```bash
cd Wish_list_telegram-bot
```
3. Создайте бота через @BotFather и получите токен.
4. В файле wishlist-bot.py замените 'YOUR_BOT_TOKEN' на ваш токен.
5. Соберите Docker-образ:
```bash
docker build -t wishlist-bot .
```
6. Запустите контейнер:
```bash
docker run -d --name wishlist-bot wishlist-bot
```

## Настройка ⚡️
Файл data.json автоматически создается при первом запуске. Структура:

```bash
{
  "gifts": [],
  "users": {},
  "admins": []
}
```
Чтобы добавить администратора:

 - Узнайте ID пользователя через бота @userinfobot

 - Внесите ID в массив admins в файле data.json

## Использование 🤖

### Для пользователей 👤

 - `/start` - главное меню

 - 🎁 Список подарков - выбрать подарок

 - 📦 Мои бронирования - управление бронями

### Для администраторов 👑

🔒 Админ-панель:

 - Добавить/удалить подарки

 - Просмотр всех бронирований

 - Управление контентом через интерактивное меню

 - `/skip` - пропустить ввод описания (при добавлении подарка)

Процесс добавления подарка:

 - Нажмите "Добавить подарок"

Введите последовательно:

 - Название подарка

 - Ссылку на товар

 - Описание (можно пропустить)

## Команды разработчика 🛠️

 - `/cancel` - отмена текущей операции

 - `/allbookings` - полный список броней (только для админов)

Логирование в файл bot.log
```bash
{
  "id": int,
  "name": "Название подарка",
  "link": "URL-ссылка",
  "description": "Описание",
  "is_booked": bool,
  "booked_by": "user_id"
}
```

## Важно ❗️

 - Файл data.json должен иметь права на запись

 - Для работы бота необходим постоянный доступ к интернету

