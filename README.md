# SF_24.7.2_LR_QAP180
У нас есть готовая библиотека с реализацией основных методов, но остались ещё два нереализованных метода. Это и будет первым практическим заданием: посмотреть документацию к имеющимся API-методам на сайте. Найти методы, которые ещё не реализованы в библиотеке, и написать их реализацию в файле api.py.
Как вы уже изучали ранее, видов тестирования много, соответственно, и тест-кейсов может быть очень много. Мы с вами написали пять простых позитивных тестов, проверяющих функционал с корректными данными, с ожидая, что всё пройдёт хорошо. Наша задача — убедиться, что система возвращает статус с кодом 200.
Но как будет реагировать тестируемое приложение, если мы в параметрах передадим слишком большое значение или вообще его не передадим? Что будет, если мы укажем неверный ключ авторизации и так далее?
Подумайте над вариантами тест-кейсов и напишите ещё 10 различных тестов для данного REST API-интерфейса. Готовые тест-кейсы разместите на GitHub и пришлите ссылку в форму ниже.

Добавлены 2 метода: 
/api/create_pet_simple
и
/api/pets/set_photo/{pet_id}
    def create_pet_simple(self, auth_key: json, name: str, animal_type: str, age: int) -> json:
        headers = {'auth_key': auth_key['key']}
        data = {
            'name': name,
            'animal_type': animal_type,
            'age': age,
        }
        res = requests.post(self.base_url + '/api/create_pet_simple', headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    def set_pet_photo(self, auth_key: json, pet_id: str, pet_photo: str) -> json:
        """ Обновить фотографию питомца по его ID """

        data = MultipartEncoder(
            fields={
                'pet_id': pet_id,
                'pet_photo': (pet_photo, open(pet_photo, 'rb'), 'image/jpeg')
            })
        headers = {'auth_key': auth_key['key'], 'Content-Type': data.content_type}

        res = requests.post(self.base_url + '/api/pets/set_photo/'  + pet_id, headers=headers, data=data)
        status = res.status_code
        result = ""
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

Добавлены простые проверки для этих методов:
def test_successful_simple_create_pet(name='Чача', animal_type='Кот', age=3):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    """Проверяем возможность простого добавления питомца (без фото)"""
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name

def test_successful_change_pet_photo():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, 'Барбоскин', 'двортерьер', '4', 'images/cat1.jpg')

    assert status == 200
    pet_id = result['id']

    status, result = pf.set_pet_photo(auth_key, pet_id, 'images/P1040103.jpg')

    assert status == 200  

Помимо этих тестов добавлены еще 10 тестов:
def test_get_all_pets_filter_my_pets():
    """ Проверяем, что можно получить только своих питомцев с фильтром 'my_pets' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 200
    assert 'pets' in result
    assert isinstance(result['pets'], list)


def test_add_new_pet_with_empty_name():
    """ Проверяем, что нельзя создать питомца с пустым именем """

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Пытаемся добавить питомца с пустым именем
    pet_photo = 'images/cat1.jpg'
    status, result = pf.add_new_pet(auth_key, '', 'собака', '2', pet_photo)

    assert status == 400  # Ожидаем, что статус ответа будет 400
    assert 'message' in result  # Проверяем, что в ответе есть сообщение об ошибке
    assert 'name' in result['message'].lower()  # Проверяем, что сообщение об ошибке связано с отсутствием имени


def test_update_pet_info_with_invalid_data():
    """ Проверяем обновление информации питомца с невалидными данными """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.update_pet_info(auth_key, pet_id, '', '', '')  # Передаем пустые значения

        assert status == 400  # Ожидаем ошибку 400
    else:
        raise Exception("There is no my pets")


def test_delete_non_existent_pet():
    """ Проверяем удаление несуществующего питомца """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pet_id = "invalid_id_asdasd"  # Неверный ID питомца
    status, result = pf.delete_pet(auth_key, pet_id)

    assert status == 404  # Ожидаем ошибку 404


def test_get_api_key_for_invalid_user(email='invalid@example.com', password='wrong_password'):
    """ Проверяем, что запрос ключа API возвращает ошибку для невалидного пользователя """

    status, result = pf.get_api_key(email, password)

    assert status != 200  # Ожидаем, что статус не равен 200
    assert 'key' not in result


def test_add_existing_pet():
    """ Проверяем обработку попытки добавить существующего питомца """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, 'Барбоскин', 'двортерьер', '4', 'images/cat1.jpg')

    assert status == 200
    pet_id = result['id']

    status, result = pf.add_new_pet(auth_key, 'Барбоскин', 'двортерьер', '4', 'images/cat1.jpg')

    assert status == 400  # Ожидаем ошибку 400 при добавлении дубликата

    # Удаляем питомца
    pf.delete_pet(auth_key, pet_id)


def test_update_pet_info_nonexistent_pet():
    """ Проверяем обновление информации для несуществующего питомца """

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.update_pet_info(auth_key, 'invalid_id_asdasd', 'name', 'type', 'age')

    assert status == 404  # Ожидаем ошибку 404


def test_add_new_pet_increases_pet_count():
    """ Проверяем, что добавление питомца увеличивает общее количество питомцев """

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Получаем текущее количество питомцев
    initial_status, initial_result = pf.get_list_of_pets(auth_key)

    assert initial_status == 200  # Ожидаем успешный ответ
    initial_count = len(initial_result['pets'])  # Сохраняем текущее количество питомцев

    # Добавляем нового питомца
    pet_photo = 'images/cat1.jpg'  # Путь к фото может быть действительным
    pf.add_new_pet(auth_key, 'Бобик', 'собака', '4', pet_photo)

    # Получаем количество питомцев после добавления
    updated_status, updated_result = pf.get_list_of_pets(auth_key)

    assert updated_status == 200  # Ожидаем успешный ответ
    updated_count = len(updated_result['pets'])  # Сохраняем новое количество питомцев

    # Проверяем, что количество питомцев увеличилось на 1
    assert updated_count == initial_count + 1


def test_create_pet_simple_with_invalid_data():
    """ Проверяем создание питомца с невалидными данными """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.create_pet_simple(auth_key, '', '', '3')  # Пустые имя и тип

    assert status == 400  # Ожидаем ошибку 400


def test_add_new_pet_with_long_name():
    """ Проверяем, что нельзя создать питомца с именем, превышающим допустимую длину """

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Создание имени превышающего допустимую длину (предположим что есть требования и ограничение 256 символов)
    long_name = 'Л' * 256
    pet_photo = 'images/cat1.jpg'  # Путь к фото может быть действительным

    # Пытаемся добавить питомца с длинным именем
    status, result = pf.add_new_pet(auth_key, long_name, 'собака', '5', pet_photo)

    assert status == 400  # Ожидаем, что статус ответа будет 400
    assert 'message' in result  # Проверяем, что в ответе есть сообщение об ошибке
    assert 'name' in result['message'].lower()  # Проверяем, что сообщение об ошибке связано с именем
