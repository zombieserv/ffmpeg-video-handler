# FFmpeg Video Handler

Тестовое задание - небольшой сервис для скачивания видео с YouTube/Torrent и локальной обработки.


## Запуск приложения

1. Убедитесь, что у вас установлен Docker и Docker Compose.

2. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/zombieserv/ffmpeg-video-handler
   cd ffmpeg-video-handler
   
3. Скопируйте файл .env и установите значения переменных окружения:
    ```bash
   cp .env.sample .env

4. Запустите Docker Compose
     ```bash
       docker-compose up --build

5. Приложение будет доступно по адресу http://localhost:5000

## Взаимодействие с сервисом
Для добавления видео в очередь на скачивание и обработку нужно отправить `POST` запрос по URL `http://localhost:5000/video`.

В теле запроса следует передать параметр `url`, он может содержать ссылку на YouTube видео, путь к локальному видеофайлу, путь к локальному *.torrent файлу или torrent magnet url.
Пример:
```json
{
  "url": "https://www.youtube.com/watch?v=g8A8DwfZsT4"
}
```

В ответе можно будет найти идентификатор добавленного видео:
```json
{
  "id": "658552fc9163cba44c9d26ea",
  "status": "success",
  "message": "Video added to queue."
}
```

Для того чтобы узнать статус добавленного в очередь видео и получить готовый результат - нужно отправить `GET` запрос по URL `http://localhost:5000/video`

В ответ вернётся подробная информация о видео:
```json
{
	"id": "658552fc9163cba44c9d26ea",
	"url": "https://www.youtube.com/watch?v=g8A8DwfZsT4",
	"name": "8 безумных экспериментов при -55°C (Самый холодный город в мире: Якутск)",
	"video_file": "videos/handled/8 безумных экспериментов при -55°C (Самый холодный город в мире Якутск)_handle.mp4",
	"status": "completed",
	"created_date": "Fri, 22 Dec 2023 09:12:28 GMT",
	"status_changed": "Fri, 22 Dec 2023 09:14:07 GMT"
}
```
**Возможные статусы:**
- `downloading` - скачивание файла
- `processing` - обработка файла
- `completed` - обработка завершена (в этом случае возвращается ссылка на обработанный файл в поле `video_file`)
- `error` - ошибка.