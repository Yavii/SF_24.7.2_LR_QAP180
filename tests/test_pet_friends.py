from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result
    print(result)


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


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
    pet_photo = 'images/cat1.jpg' 
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
    pet_photo = 'images/cat1.jpg' 

    # Пытаемся добавить питомца с длинным именем
    status, result = pf.add_new_pet(auth_key, long_name, 'собака', '5', pet_photo)

    assert status == 400  # Ожидаем, что статус ответа будет 400
    assert 'message' in result  # Проверяем, что в ответе есть сообщение об ошибке
    assert 'name' in result['message'].lower()  # Проверяем, что сообщение об ошибке связано с именем

