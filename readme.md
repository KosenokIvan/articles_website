# Сайт со статьями

## Сборка и запуск

 1. Скачать и распаковать архив с проектом
 2. В папке с проектом выполнить команду
  
        pip install -r requirements.txt

 3. Запустить файл main.py

        python main.py

 4. Перейти по адресу <http://localhost:5000/>

## Краткое описание

**Техническое задание**: Создание сайта, на котором пользователи могли бы публиковать свои статьи

**Возможности**: Регистрация, авторизация, добавление, изменение и удаление статей и комментариев
к ним, добавление и удаление лайков на статьи. К профилям пользователей, статьям и комментариям 
можно прикреплять по одному изображению. Модераторы могут удалять записи и комментарии других 
пользователей, администраторы могут выдавать и отбирать модераторские права, а также удалять статьи 
и комментарии модераторов

**Возможности API**: Возможности, перечисленные выше + ряд возможностей по сортировке и фильтрации 
пользователей и статей

## Администрация

### Выдача прав администратора
В папке проекта выполнить команду:

    python manage.py give_admin_rights <id пользователя>

____

### Лишение прав администратора
В папке проекта выполнить команду:

    python manage.py revoke_admin_rights <id пользователя>

## API документация

### Пользователи

#### Авторизация

    POST /api/login

JSON аргументы:

 - email: str
 - password: str
 - \[remember_me: bool (default=False)\]

Возвращаемый JSON: *\*Стандартный JSON, возвращаемый библиотекой flask-restful при отсутствии или 
некорректном значении аргументов, здесь и далее в документации не указан*

 - Успех

        200 {"success": "ok"}

 - Неверная почта или пароль:

        404 {"message": "Incorrect email or password"}

____

#### Выход из аккаунта *\(login required\)*

    POST /api/logout

Возвращаемый JSON:

 - Успех

        200 {"success": "ok"}

 - Авторизация отсутствует *\(Может быть возвращено в ответ на любой запрос, требующий авторизацию, 
   далее в документации указываться не будет\)*
   
        401 {"message": "Authorization required"}

____

#### Регистрация

    POST /api/users

JSON аргументы:

 - name: str
 - surname: str
 - nickname: str
   
    - Длина от 3 до 32 символов
    - Может содержать только латинские буквы любого регистра без диакритических знаков, 
      цифры и знаки подчёркивания
    
 - email: str
   
    - Используется только для авторизации и не отображается на странице
   
 - password: str
    - Длина от 8 до 512 символов
    - Должен содержать хотя бы один непробельный символ 
 - password_again: str
 - \[description: str\]
 - \[avatar: str\]

    - Изображение в hex формате
    - Поддерживаемые форматы: png, jpg, jpeg
    - Успешное добавление изображения другого формата не 
      гарантируется, но и не исключено \(В частности было успешно протестировано 
      добавление gif изображения\)
    - Изображение на стороне сервера преобразуется в png формат независимо от исходного типа
    
Возвращаемый JSON:

 - Успех

        200 {"success": "ok"}

 - Пароли не совпадают

        400 {"message": "Password mismatch"}

 - Никнейм уже занят другим пользователем

        400 {"message": "User already exists"}

 - Уже существует аккаунт с данным адресом почты

        400 {"message": "Email already use"}

 - Некорректный формат почты

        400 {"message": "Incorrect email format"}

 - Длина никнейма не соответствует необходимому диапазону

        400 {"message": "Length of the nickname must be between 3 and 32"}

 - Никнейм содержит недопустимые символы

        400 {"message": "Nickname contains invalid characters"}

 - Длина пароля не соответствует необходимому диапазону

        400 {"message": "Length of password must be between 8 and 512"}

 - Пароль не содержит непробельных символов

        400 {"message": "Password must contain at least 1 non-whitespace character"}

 - Ошибка при работе с изображением \(скорее всего был прислан файл, не являющийся изображением\)

        400 {"message": "Incorrect image"}

____

#### Получение информации о пользователе

    GET /api/user/<int:user_id>

GET аргументы

 - \[get_field: list\(str\) \(choices=\["id", "**name**", "**surname**", "nickname", "**email**", 
   "description", "avatar", "**modified_date**", "is_moderator", "is_admin"\], 
   default=\["id", "nickname"\]\)\]
    - Информацию о значении выделенных жирным полей может получить только авторизованный 
      пользователь и только о своём аккаунте
    - Если все указанные в запросе поля будут недоступны, в ответе будет прислано только id

Возвращаемый JSON

 - Успех

        200 {"user": {field.name: field.value for field in get_field}}

 - Пользователь не найден

        404 {"message": "User not found"}

____

#### Изменение пользователя *\(login required\)*

    PUT /api/user/<int:user_id>

JSON аргументы

 - \[name: str\]
 - \[surname: str\]
 - \[nickname: str\]
 - \[email: str\]
 - \[new_password: str\]
 - \[new_password_again: str\]
 - \[description: str\]
 - \[avatar: str\]
 - password: str
   
    - Текущий пароль для подтверждения изменений
   
Возвращаемый JSON

 - См. Возвращаемый JSON в запросе регистрации
 - Запрещено (попытка редактировать чужую страницу)

        403 {"message": "Forbidden"}

 - Некорректный пароль

        400 {"message": "Incorrect password"}

____

#### Удаление пользователя *\(login required\)*

    DELETE /api/user/<int:user_id>

JSON аргументы

 - password: str
  
    - Текущий пароль для подтверждения удаления
   
Возвращаемый JSON

 - Успех

        200 {"success": "ok"}   

 - Запрещено (попытка удалить чужую страницу)
   
        403 {"message": "Forbidden"}

 - Пользователь не найден
   
        404 {"message": "User not found"}

 - Некорректный пароль

        400 {"message": "Incorrect password"}

____

#### Получение информации о списке пользователей

    GET /api/users

GET аргументы

 - \[limit: int\]
 - \[offset: int\]
 - \[nickname_search_string: str\]
 - \[nickname_filter: str \(choices=\["equals", "equals_case_insensitive", "starts", 
   "ends", "contains"\], default="equals"\)\]
   - equals \- полное соответствие с учётом регистра
   - equals_case_insensitive \- равенство без учёта регистра
   - starts \- никнейм начинается с данной строки, без учёта регистра
   - ends \- никнейм заканчивается на данную строку, без учёта регистра
   - contains \- никнейм содержит данную строку, без учёта регистра
 - \[get_field: list\(str\) \(choices=\["id", "nickname", "description", "avatar"\], 
   default=\["id", "nickname"\]\)\]
   
Возвращаемый JSON

 - Успех

        200 {"users": [{field.name: field.value for field in get_field} for user in users]}

____

### Статьи

#### Получение информации о статье

    GET /api/article/<int:article_id>

GET аргументы

 - \[get_field: list\(str\) \(choices=\["id", "title", "content", "image", "author", 
   "likes_count", "create_date"\], default=\["id", "title"\]\)\]
   
Возвращаемый JSON

 - Успех

        200 {"article": {field.name: field.value for field in get_field}}

 - Статья не найдена

        404 {"message": "Article not found"}

____

#### Изменение статьи *\(login required\)*

    PUT /api/article/<int:article_id>

JSON аргументы

 - \[title: str\]
 - \[content: str\]
 - \[image: str\]

Возвращаемый JSON

 - Успех
   
        200 {"success": "ok"}

 - Статья не найдена
   
        404 {"message": "Article not found"}

 - Запрещено
   
        403 {"message": "Forbidden"}

 - Ошибка при обработке изображения

        400 {"message": "Incorrect image"}

____

#### Удаление статьи *\(login required\)*

    DELETE /api/article/<int:article_id>

Возвращаемый JSON

 - Успех
   
        200 {"success": "ok"}

 - Статья не найдена
   
        404 {"message": "Article not found"}

 - Запрещено
   
        403 {"message": "Forbidden"}

____

#### Добавление статьи *\(login required\)*

    POST /api/articles

JSON аргументы

 - \[title: str\]
 - \[content: str\]
 - \[image: str\]

Возвращаемый JSON

 - Успех
   
        200 {"success": "ok"}

 - Ошибка при обработке изображения

        400 {"message": "Incorrect image"}

____

#### Получение информации о списке статей

    GET /api/articles

GET аргументы

 - \[limit: int\]
 - \[offset: int\]
 - \[sorted_by: str \(choices=\["create_date", "likes_count"\], default="create_date"\)\]
 - \[int: author\]
 - \[get_field: list\(str\) \(choices=\["id", "title", "content", "image", 
   "author", "likes_count", "create_date"\], default=\["id", "title"\]\)\]
   
Возвращаемый JSON

 - Успех

        200 {"articles": [{field.name: field.value for field in get_field} for article in articles]}

____

### Комментарии

#### Получение информации о комментарии

    GET /api/comment/<int:comment_id>

GET аргументы

 - \[get_field: list\(str\) \(choices=\["id", "author", "article_id", "image", "text", "create_date"\], default=\["id", "author", "content"\]\)\]

Возвращаемый JSON

 - Успех
   
        200 {"comment": {field.name: field.value for field in get_field}}

 - Комментарий не найден

        404 {"message": "Comment not found"}

____

#### Изменение комментария *\(login required\)*

    PUT /api/comment/<int:comment_id>

JSON аргументы

 - \[text: str\]
 - \[image: str\]

Возвращаемый JSON

 - Успех
   
        200 {"success": "ok"}

 - Комментарий не найден
   
        404 {"message": "Comment not found"}

 - Запрещено
   
        403 {"message": "Forbidden"}

 - Ошибка при работе с изображением

        400 {"message": "Incorrect image"}

____

#### Удаление комментария *\(login required\)*

    DELETE /api/comment/<int:comment_id>

Возвращаемый JSON

 - Успех
   
        200 {"success": "ok"}

 - Комментарий не найден
   
        404 {"message": "Comment not found"}

 - Запрещено

        403 {"message": "Forbidden"}

____

#### Добавление комментария *\(login required\)*

    POST /api/comments

JSON аргументы:

 - text:  str
 - article_id: int
 - \[image: str\]

Возвращаемый JSON

 - Успех
   
        200 {"success": "ok"}

 - Статья не найдена
   
        404 {"message": "Article not found"}

 - Ошибка при обработке изображения

        400 {"message": "Incorrect image"}

____

#### Получение информации о списке комментариев

    GET /api/comments

GET аргументы

 - \[limit: int\]
 - \[offset: int\]
 - \[author: int\]
 - \[article_id: int\]
 - \[get_field: list\(str\) \(choices=\["id", "author", "article_id", "image", 
   "text", "create_date"\], default=\["id", "author", "article_id"\]\)\]
   
Возвращаемый JSON

 - Успех

        200 {"comments": [{field.name: field.value for field in get_field} for comment in comments]}

____

### Лайки

#### Проверка, поставлен ли лайк *\(login required\)*

    GET /api/like/<int:article_id>

Возвращаемый JSON

 - Успех

        200 {"like_exist": <Текущий пользователь поставил лайк на запись: bool>}

____

#### Поставить лайк *\(login required\)*

    POST /api/like/<int:article_id>

Возвращаемый JSON

 - Успех
   
        200 {"success": "ok"}

 - Статья не найдена
   
        404 {"message": "Article not found"}

 - Лайк уже поставлен

        400 {"message": "Like already there"}

____

#### Убрать лайк *\(login required\)*

    DELETE /api/like/<int:article_id>

Возвращаемый JSON

 - Успех
   
        200 {"success": "ok"}

 - Статья не найдена
   
        404 {"message": "Article not found"}

 - Лайк отсутствует

        404 {"message": "Like not found"}

____

### Пример использования API

    from io import BytesIO
    from PIL import Image
    from requests import get, post, put, delete
    

    def image_to_byte_array(image_filename):
        image = Image.open(image_filename)
        image_byte_array = BytesIO()
        image.save(image_byte_array, format="PNG")
        return image_byte_array.getvalue()

    
    EMAIL = ...
    PASSWORD = ...
    NICKNAME = ...
    AVATAR_FILENAME = ...

    register_response = post("http://localhost:5000/api/users", json={
        "name": "name",
        "surname": "surname",
        "nickname": NICKNAME,
        "email": EMAIL,
        "password": PASSWORD,
        "password_again": PASSWORD,
        "avatar": image_to_byte_array(AVATAR_FILENAME).hex()
    })
    print(register_response.json())
    if not register_response:
        exit()

    get_id_response = get(f"http://localhost:5000/api/users?"
                          f"nickame_search_string={NICKNAME}&get_field=id").json()
    print(get_id_response)
    if not get_id_response:
        exit()
    id = get_id_response["users"][0]["id"]

    print(get(f"http://localhost:5000/api/user/{id}?get_field=email&get_field=description").json())

    login_response = post("http://localhost:5000/api/login", json={
        "email": EMAIL,
        "password": PASSWORD
    })
    print(login_response.json())
    if not login_response:
        exit()

    print(get(f"http://localhost:5000/api/user/{id}?get_field=email&get_field=description",
              cookies=login_response.cookies).json())

    print(delete(f"http://localhost:5000/api/user/{id}", json={
        "password": PASSWORD
    }).json())
    print(delete(f"http://localhost:5000/api/user/{id}", json={
        "password": PASSWORD
    }, cookies=login_response.cookies).json())
