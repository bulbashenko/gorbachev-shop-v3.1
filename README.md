# Техническое задание для gorbachev.shop


## Cодержание
- [Техническое задание для gorbachev.shop](#техническое-задание-для-gorbachevshop)
  - [Cодержание](#cодержание)
  - [1. Обзор проекта](#1-обзор-проекта)
  - [2. Члены команды](#2-члены-команды)
  - [3. Технологический стек](#3-технологический-стек)
  - [4. Ключевые функции](#4-ключевые-функции)
  - [5. Роли пользователей](#5-роли-пользователей)
  - [6. Варианты доставки](#6-варианты-доставки)
  - [7. Специфические интеграции](#7-специфические-интеграции)
    - [Поддерживаемые провайдеры](#поддерживаемые-провайдеры)
    - [Функциональные требования](#функциональные-требования)
    - [Детали реализации](#детали-реализации)
    - [Пример API Workflow](#пример-api-workflow)
    - [Безопасность](#безопасность)
    - [UI Компоненты](#ui-компоненты)
  - [8. Обзор архитектуры](#8-обзор-архитектуры)
    - [Frontend](#frontend)
    - [Backend](#backend)
    - [Деплоймент](#деплоймент)
  - [9. Дизайн базы данных](#9-дизайн-базы-данных)
    - [Сущности и связи](#сущности-и-связи)
  - [10. API Endpoints](#10-api-endpoints)
    - [Аутентификация](#аутентификация)
    - [Профиль пользователя](#профиль-пользователя)
    - [Продукты](#продукты)
    - [Категории](#категории)
    - [Корзина](#корзина)
    - [Заказы](#заказы)
    - [Списки желаний](#списки-желаний)
    - [Отзывы](#отзывы)
    - [Варианты доставки](#варианты-доставки)
    - [Адреса](#адреса)
  - [11. Компоненты пользовательского интерфейса](#11-компоненты-пользовательского-интерфейса)
    - [Публичные страницы](#публичные-страницы)
    - [Страницы для авторизованных пользователей](#страницы-для-авторизованных-пользователей)
    - [Процесс оформления заказа](#процесс-оформления-заказа)
    - [Административная панель](#административная-панель)
  - [12. Дополнительные заметки](#12-дополнительные-заметки)
    - [Безопасность](#безопасность-1)
    - [Оптимизация производительности](#оптимизация-производительности)
    - [Доступность](#доступность)
    - [Тестирование и QA](#тестирование-и-qa)
    - [Документация](#документация)
  - [13. Обязанности](#13-обязанности)
    - [Frontend-разработчик (**bulbashenko**)](#frontend-разработчик-bulbashenko)
    - [Backend-разработчик (**nadeko**)](#backend-разработчик-nadeko)
  - [14. Коммуникация и сотрудничество](#14-коммуникация-и-сотрудничество)
  - [15. Открытые вопросы и предположения](#15-открытые-вопросы-и-предположения)

---

## 1. Обзор проекта

**Название проекта**: gorbachev.shop

gorbachev.shop — это платформа электронной коммерции, специализирующаяся на продаже кастомной одежды и небольших аксессуаров. Платформа нацелена на предоставление пользователям бесшовного опыта покупок, позволяя им настраивать продукты, управлять заказами и пользоваться безопасными вариантами оплаты и доставки.

---

## 2. Члены команды

- **Frontend-разработчик**: **bulbashenko**
- **Backend-разработчик**: **nadeko**

---

## 3. Технологический стек

- **Frontend-фреймворк**: Next.js 15
- **CSS-фреймворк**: Tailwind CSS
- **UI-библиотеки**: Headless UI 2.1
- **Управление состоянием**: Redux Toolkit
- **Backend-фреймворк**: FastAPI
- **База данных**: PostgreSQL
- **Хэширование паролей**: bcrypt
- **Платежный шлюз**: Stripe (предположительно)
- **Система контроля версий**: Git (GitHub)
- **Деплоймент**: Docker, Kubernetes (опционально), AWS/GCP/Azure (подлежит выбору)

---

## 4. Ключевые функции

1. **Аутентификация и авторизация пользователей**
   - Регистрация и вход пользователя (email/пароль)
   - Вход через социальные сети (Google, Facebook)
   - Восстановление и сброс пароля

2. **Каталог продуктов**
   - Отображение продуктов с высококачественными изображениями
   - Категории и подкатегории
   - Расширенный поиск, фильтрация и сортировка

3. **Кастомизация продуктов**
   - Настройка предметов одежды (размер, цвет, загрузка текста/изображений)
   - Предварительный просмотр настроек в реальном времени

4. **Корзина**
   - Добавление, удаление и обновление товаров
   - Сохранение корзины для дальнейшего использования
   - Применение скидочных кодов или акций

5. **Процесс оформления заказа**
   - Возможность оформления заказа без регистрации
   - Множественные адреса доставки
   - Обработка платежей через Stripe

6. **Управление заказами**
   - История и детали заказов
   - Отслеживание заказов
   - Отмена и возвраты

7. **Список желаний**
   - Сохранение избранных продуктов
   - Возможность поделиться списком желаний

8. **Отзывы и рейтинги**
   - Оставление отзывов и рейтингов на продукты
   - Жалобы на неподобающий контент

9. **Административная панель**
   - Управление продуктами, заказами, пользователями и отзывами
   - Управление инвентарем
   - Аналитика и отчеты

10. **Уведомления**
    - Email-подтверждения для заказов, обновления по доставке
    - Маркетинговые рассылки (опционально)

11. **Адаптивный дизайн**
    - Мобильный подход в первую очередь
    - Совместимость со всеми основными браузерами

12. **Функции безопасности**
    - SSL-шифрование
    - Соответствие требованиям по защите данных и конфиденциальности (например, GDPR)

---

## 5. Роли пользователей

1. **Гость**
   - Просмотр продуктов
   - Добавление товаров в корзину
   - Оформление заказа без регистрации
   - Просмотр публичных страниц (FAQ, Контакты)

2. **Зарегистрированный пользователь**
   - Все возможности гостя
   - Доступ к личному кабинету
   - Управление профилем и адресами
   - Просмотр истории заказов
   - Создание и управление списками желаний
   - Оставление отзывов и рейтингов

3. **Администратор**
   - Полный доступ к административной панели
   - Управление продуктами, категориями и инвентарем
   - Обработка заказов и управление возвратами
   - Управление пользователями и их правами
   - Просмотр аналитики и создание отчетов
   - Настройка параметров сайта и интеграций

---

## 6. Варианты доставки

1. **Стандартная доставка**
   - Доставка в течение 5-7 рабочих дней
   - Фиксированная ставка или цена на основе веса

2. **Экспресс-доставка**
   - Доставка в течение 1-3 рабочих дней
   - Дополнительная стоимость в зависимости от местоположения и веса

3. **Международная доставка**
   - Сроки доставки зависят от пункта назначения
   - Могут применяться таможенные пошлины
   - Список поддерживаемых стран необходимо уточнить

4. **Самовывоз**
   - Возможность для клиентов забрать заказы из физического магазина (если применимо)

---

## 7. Специфические интеграции

1. **Платежный шлюз**
   - **Stripe** для безопасной обработки платежей.
   - Поддержка основных кредитных/дебетовых карт и цифровых кошельков.
   - API Stripe для управления платежами, возвратами и подтверждением транзакций.

2. **Email-сервис**
   - Интеграция с **SendGrid** или **Mailchimp** для транзакционных и маркетинговых email.

3. **Аналитика**
   - **Google Analytics** для анализа трафика и поведения пользователей.
   - **Google Tag Manager** для управления кодами отслеживания.

4. **Социальные сети**
   - OAuth-интеграция для входа через социальные сети (Google, Facebook).
   - Кнопки поделиться на страницах продуктов.

5. **Управление контентом**
   - Интеграция с headless CMS, например, **Contentful**, для управления некаталоговым контентом (опционально).

6. **Поддержка клиентов**
   - Онлайн-чат через **Intercom** или **Zendesk** (опционально).

7. ### OAuth Интеграция

**Цель**: Реализация бесшовного входа пользователей через сторонние платформы аутентификации. Это упростит процесс регистрации, уменьшит барьеры входа и улучшит пользовательский опыт.

### Поддерживаемые провайдеры
1. **Google** (через Google Identity Services)
2. **Facebook** (через Facebook Login)
3. **Apple** (через Sign in with Apple)

---

### Функциональные требования

1. **Регистрация и вход через OAuth**:
   - Возможность регистрации новых пользователей через учетные записи Google, Facebook или Apple.
   - Вход для уже существующих пользователей, связанных с учетными записями.

2. **Связывание учетных записей**:
   - Опция для зарегистрированных пользователей связать свои аккаунты с OAuth-провайдерами в личном кабинете.

3. **Обработка токенов и безопасности**:
   - Валидация и безопасное хранение токенов OAuth.
   - Токены доступа и обновления не должны сохраняться на клиентской стороне.

4. **Дополнительные данные**:
   - Сбор основных данных от провайдеров (имя, email, изображение профиля).
   - Запрос разрешений только на минимально необходимый набор данных.

5. **Обработка ошибок**:
   - Уведомления об отказе в доступе, истечении токена или ошибках провайдера.

---

### Детали реализации

1. **Google Identity Services**:
   - **API**: OAuth 2.0 и OpenID Connect.
   - **Данные пользователя**:
     - `name`: имя пользователя.
     - `email`: адрес электронной почты.
     - `picture`: URL аватара.
   - **Scopes**: `openid`, `email`, `profile`.

2. **Facebook Login**:
   - **API**: Graph API.
   - **Данные пользователя**:
     - `name`: имя пользователя.
     - `email`: адрес электронной почты (если разрешено).
     - `picture`: URL изображения профиля.
   - **Scopes**: `public_profile`, `email`.

3. **Sign in with Apple**:
   - **API**: Apple OAuth 2.0.
   - **Особенности**:
     - Email может быть скрыт пользователем; при этом Apple предоставляет `relay email`.
     - Использование JWT для передачи данных пользователя.
   - **Данные пользователя**:
     - `name`: имя пользователя.
     - `email`: реальный или скрытый адрес электронной почты.
   - **Scopes**: `name`, `email`.

---

### Пример API Workflow

1. **Frontend**:
   - Пользователь нажимает кнопку входа через Google, Facebook или Apple.
   - Получение авторизационного токена с помощью SDK провайдера.

2. **Backend**:
   - Получение токена авторизации от клиента.
   - Проверка токена на сервере через API провайдера.
   - Если пользователь новый:
     - Создание учетной записи с данными от провайдера.
   - Если пользователь существует:
     - Проверка совпадения email и авторизация.

3. **Хранение данных**:
   - Ассоциация учетной записи с ID провайдера (`provider_user_id`) для каждой платформы.
   - Таблица для OAuth-связей:
     - `oauth_id` (PK).
     - `user_id` (FK).
     - `provider_name` (Google/Facebook/Apple).
     - `provider_user_id` (уникальный).
     - `access_token` (зашифрованный).
     - `refresh_token` (зашифрованный).
     - Временные метки.

---

### Безопасность

- Хранение токенов доступа/обновления на сервере (шифрование).
- Использование HTTP-only cookies для передачи токенов аутентификации.
- Регулярная ревокация истекших токенов.

---

### UI Компоненты

1. **Кнопки входа**:
   - Дизайн кнопок в соответствии с рекомендациями провайдеров.
   - Примеры текста:
     - "Sign in with Google".
     - "Continue with Facebook".
     - "Sign in with Apple".

2. **Процесс**:
   - Отображение уведомлений при успешной/неудачной попытке входа.
   - Опция связать аккаунты через страницу "Настройки профиля".

---

Это добавляет четкости к реализации OAuth и упрощает интеграцию.

---

## 8. Обзор архитектуры

### Frontend

- **Next.js 15**
  - Рендеринг на стороне сервера для оптимизации SEO
  - Динамическая маршрутизация для страниц продуктов и категорий
- **Tailwind CSS**
  - CSS-фреймворк с утилитарным подходом для быстрой разработки UI
- **Управление состоянием**
  - Использование React Context или Redux для глобального состояния
- **Аутентификация**
  - JWT-токены, хранящиеся в HTTP-only cookies для безопасности

### Backend

- **FastAPI**
  - Разработка RESTful API
  - Высокая производительность и поддержка асинхронных операций
- **База данных**
  - **PostgreSQL** для реляционных данных
  - Использование ORM, например, SQLAlchemy
- **Кэширование**
  - **Redis** для кэширования часто запрашиваемых данных (опционально)
- **Документация API**
  - Автоматическая документация с помощью **Swagger/OpenAPI**

### Деплоймент

- **Контейнеризация**
  - Docker для контейнеризации приложений
- **Оркестрация**
  - Kubernetes для управления контейнерами (при необходимости масштабирования)
- **CI/CD**
  - Интеграция с GitHub Actions или Jenkins

---

## 9. Дизайн базы данных

### Сущности и связи

- **Пользователи**
  - `user_id` (PK)
  - `email` (уникальный)
  - `password_hash`
  - `first_name`
  - `last_name`
  - `phone_number`
  - `role` (user, admin)
  - Временные метки

- **Продукты**
  - `product_id` (PK)
  - `name`
  - `description`
  - `price`
  - `sku`
  - `category_id` (FK)
  - `inventory_count`
  - `customizable` (boolean)
  - Временные метки

- **Категории**
  - `category_id` (PK)
  - `name`
  - `parent_category_id` (FK, nullable)
  - Временные метки

- **Заказы**
  - `order_id` (PK)
  - `user_id` (FK)
  - `total_amount`
  - `status` (pending, confirmed, shipped, delivered, cancelled)
  - `shipping_address_id` (FK)
  - Временные метки

- **Позиции заказа**
  - `order_item_id` (PK)
  - `order_id` (FK)
  - `product_id` (FK)
  - `quantity`
  - `price`
  - `customization_details` (JSON, nullable)

- **Элементы корзины**
  - `cart_item_id` (PK)
  - `user_id` (FK)
  - `product_id` (FK)
  - `quantity`
  - `customization_details` (JSON, nullable)
  - Временные метки

- **Списки желаний**
  - `wishlist_id` (PK)
  - `user_id` (FK)
  - Временные метки

- **Элементы списка желаний**
  - `wishlist_item_id` (PK)
  - `wishlist_id` (FK)
  - `product_id` (FK)
  - Временные метки

- **Отзывы**
  - `review_id` (PK)
  - `user_id` (FK)
  - `product_id` (FK)
  - `rating` (1-5)
  - `comment`
  - Временные метки

- **Адреса**
  - `address_id` (PK)
  - `user_id` (FK)
  - `street_address`
  - `city`
  - `state`
  - `zip_code`
  - `country`
  - Временные метки

- **Варианты доставки**
  - `shipping_option_id` (PK)
  - `name`
  - `description`
  - `cost`
  - `estimated_delivery_time`
  - Временные метки

---

## 10. API Endpoints

### Аутентификация

- **POST** `/api/auth/register`
  - Регистрация нового пользователя
- **POST** `/api/auth/login`
  - Вход пользователя и генерация токена
- **POST** `/api/auth/logout`
  - Завершение сессии пользователя
- **POST** `/api/auth/password-reset`
  - Инициировать сброс пароля
- **POST** `/api/auth/password-reset/confirm`
  - Подтверждение сброса пароля

### Профиль пользователя

- **GET** `/api/users/me`
  - Получить профиль текущего пользователя
- **PUT** `/api/users/me`
  - Обновить профиль пользователя

### Продукты

- **GET** `/api/products`
  - Список продуктов с пагинацией и фильтрами
- **GET** `/api/products/{product_id}`
  - Получить детали продукта
- **POST** `/api/products`
  - Создать новый продукт (только для администратора)
- **PUT** `/api/products/{product_id}`
  - Обновить продукт (только для администратора)
- **DELETE** `/api/products/{product_id}`
  - Удалить продукт (только для администратора)

### Категории

- **GET** `/api/categories`
  - Список всех категорий
- **GET** `/api/categories/{category_id}`
  - Получить детали категории

### Корзина

- **GET** `/api/cart`
  - Получить элементы корзины текущего пользователя
- **POST** `/api/cart`
  - Добавить товар в корзину
- **PUT** `/api/cart/{cart_item_id}`
  - Обновить количество или настройки товара в корзине
- **DELETE** `/api/cart/{cart_item_id}`
  - Удалить товар из корзины

### Заказы

- **GET** `/api/orders`
  - Список заказов пользователя
- **GET** `/api/orders/{order_id}`
  - Получить детали заказа
- **POST** `/api/orders`
  - Создать новый заказ
- **PUT** `/api/orders/{order_id}/cancel`
  - Отменить заказ (если применимо)

### Списки желаний

- **GET** `/api/wishlists`
  - Получить список желаний пользователя
- **POST** `/api/wishlists`
  - Создать список желаний (если разрешены множественные списки)
- **POST** `/api/wishlists/{wishlist_id}/items`
  - Добавить товар в список желаний
- **DELETE** `/api/wishlists/{wishlist_id}/items/{wishlist_item_id}`
  - Удалить товар из списка желаний

### Отзывы

- **POST** `/api/reviews`
  - Оставить отзыв
- **GET** `/api/reviews/product/{product_id}`
  - Получить отзывы о продукте

### Варианты доставки

- **GET** `/api/shipping-options`
  - Список доступных вариантов доставки

### Адреса

- **GET** `/api/addresses`
  - Список сохраненных адресов пользователя
- **POST** `/api/addresses`
  - Добавить новый адрес
- **PUT** `/api/addresses/{address_id}`
  - Обновить адрес
- **DELETE** `/api/addresses/{address_id}`
  - Удалить адрес

---

## 11. Компоненты пользовательского интерфейса

### Публичные страницы

- **Главная страница**
  - Рекомендуемые продукты и акции
- **Страница каталога**
  - Отображает продукты с фильтрами
- **Страница продукта**
  - Информация о продукте и настройки
- **О нас, Контакты, FAQ**
  - Статические информационные страницы

### Страницы для авторизованных пользователей

- **Личный кабинет**
  - Обзор активности пользователя
- **Настройки профиля**
  - Обновление личной информации
- **История заказов**
  - Просмотр прошлых заказов и их статусов
- **Список желаний**
  - Управление сохраненными продуктами
- **Корзина**
  - Просмотр товаров перед оформлением заказа

### Процесс оформления заказа

- **Информация о доставке**
  - Ввод или выбор адреса доставки
- **Информация об оплате**
  - Ввод платежных данных или выбор сохраненного метода
- **Обзор заказа**
  - Финальный просмотр перед размещением заказа
- **Подтверждение заказа**
  - Отображается после успешного размещения заказа

### Административная панель

- **Обзор**
  - Статистика продаж и уведомления
- **Управление продуктами**
  - Добавление, редактирование или удаление продуктов
- **Управление заказами**
  - Просмотр и обработка заказов
- **Управление пользователями**
  - Управление аккаунтами и правами пользователей
- **Управление контентом**
  - Редактирование статических страниц и контента сайта

---

## 12. Дополнительные заметки

### Безопасность

- **Защита данных**
  - Шифрование конфиденциальных данных в транзите и на хранении.
- **Соответствие требованиям**
  - Соответствие GDPR и CCPA в отношении данных пользователей.
- **Аутентификация**
  - Реализация многофакторной аутентификации для администраторов.
- **Content Security Policy (CSP)**
  - Использование CSP для предотвращения загрузки подозрительных ресурсов и скриптов.
- **Защита от XSS**
  - Реализация механизмов для предотвращения атак XSS.
- **Безопасность API**
  - Защита эндпоинтов с использованием токенов доступа и ограничений IP-адресов.

---
### Оптимизация производительности

- **Кэширование**
  - Использование CDN для статических ресурсов
  - Реализация кэширования на стороне сервера для ответов API
- **Отложенная загрузка**
  - Загрузка изображений и компонентов по мере необходимости

### Доступность

- **Стандарты**
  - Соблюдение руководств WCAG 2.1
- **Тестирование**
  - Использование инструментов тестирования доступности во время разработки

### Тестирование и QA

- **Модульные тесты**
  - Для backend API и frontend компонентов
- **Интеграционные тесты**
  - Сквозное тестирование пользовательских потоков
- **Автоматизированное тестирование**
  - Реализация CI/CD-пайплайна с автоматизированными тестами

### Документация

- **Документация кода**
  - Использование docstrings и комментариев
- **Документация API**
  - Поддержание актуальных спецификаций Swagger/OpenAPI
- **Руководства пользователя**
  - Создание инструкций для административных функций

---

## 13. Обязанности

### Frontend-разработчик (**bulbashenko**)

- Разработка адаптивных UI-компонентов с использованием Next.js и Tailwind CSS
- Реализация клиентской маршрутизации и управления состоянием
- Интеграция frontend с backend API
- Оптимизация для SEO и производительности
- Обеспечение кросс-браузерной совместимости

### Backend-разработчик (**nadeko**)

- Проектирование и реализация RESTful API с использованием FastAPI
- Разработка схем базы данных и управление миграциями
- Реализация механизмов аутентификации и авторизации
- Интеграция сторонних сервисов (Stripe, SendGrid)
- Обеспечение безопасности и масштабируемости API

---

## 14. Коммуникация и сотрудничество

- **Система контроля версий**
  - Использование Git с стратегией ветвления (например, GitFlow)
- **Управление проектом**
  - Использование инструментов типа **Trello** или **Jira** для отслеживания задач
- **Каналы коммуникации**
  - **Slack** для ежедневной коммуникации
  - **Еженедельные встречи** через Zoom или Google Meet
- **Документация**
  - Ведение общего пространства в **Confluence** или рабочей области **Notion**

---

## 15. Открытые вопросы и предположения

- **Подтверждение платежного шлюза**
  - Ожидается окончательное решение по использованию Stripe или альтернативы
- **Детали доставки**
  - Необходимо уточнить страны международной доставки и тарифы
- **Сторонние сервисы**
  - Решить по опциональным интеграциям (онлайн-чат, CMS)
- **Контент и медиа**
  - Источники и лицензирование изображений и видео
- **Юридические требования**
  - Разработка условий использования и политики конфиденциальности

---
