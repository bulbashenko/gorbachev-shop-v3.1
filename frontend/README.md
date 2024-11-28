# Gorbachev.shop

Structure:
```
gorbachev-shop-v3-main/
├── .eslintrc.json          # Конфигурация ESLint для проверки качества кода.
├── .gitignore              # Список файлов и папок, которые игнорируются Git.
├── LICENSE                 # Лицензионное соглашение для проекта.
├── README.md               # Основное описание проекта.
├── next.config.ts          # Конфигурация Next.js. [Документация](https://nextjs.org/docs/api-reference/next.config.js/introduction)
├── package-lock.json       # Файл блокировки npm-зависимостей.
├── package.json            # Список зависимостей и скриптов проекта. [Документация](https://docs.npmjs.com/cli/v9/configuring-npm/package-json)
├── postcss.config.mjs      # Конфигурация для PostCSS. [Документация](https://nextjs.org/docs/advanced-features/customizing-postcss-config)
├── tailwind.config.ts      # Конфигурация для TailwindCSS. [Документация](https://tailwindcss.com/docs/configuration)
├── tsconfig.json           # Конфигурация TypeScript. [Документация](https://nextjs.org/docs/basic-features/typescript)
├── messages/               # Содержит файлы локализации для разных языков.
│   ├── en.json             # Английская локализация.
│   ├── ru.json             # Русская локализация.
│   └── sk.json             # Словацкая локализация.
└── src/
    ├── middleware.ts       # Middleware для обработки запросов. [Документация](https://nextjs.org/docs/advanced-features/middleware)
    ├── app/
    │   ├── layout.tsx      # Главный layout приложения. [Документация](https://nextjs.org/docs/app/building-your-application/routing/pages-and-layouts)
    │   ├── not-found.tsx   # Страница 404 для всего приложения. [Документация](https://nextjs.org/docs/app/building-your-application/routing/custom-error-page)
    │   ├── [locale]/       # Локализованные маршруты.
    │   │   ├── globals.css # Глобальные стили.
    │   │   ├── layout.tsx  # Layout для локализованного маршрута.
    │   │   ├── not-found.tsx # 404 для локализованного маршрута.
    │   │   ├── page.tsx    # Главная страница для локализованного маршрута.
    │   │   ├── [...rest]/page.tsx # Обработка динамических маршрутов. [Документация](https://nextjs.org/docs/app/building-your-application/routing/dynamic-routes)
    │   │   ├── components/ # Компоненты для локализованного интерфейса.
    │   │   │   ├── header.tsx         # Заголовок сайта.
    │   │   │   ├── navigation-menu.tsx # Навигационное меню.
    │   │   │   ├── theme-provider.tsx # Провайдер для темы (светлая/темная).
    │   │   │   └── theme-switcher.tsx # Переключатель тем.
    │   │   └── utils/
    │   │       └── navigationLinks.tsx # Массив ссылок для навигации.
    └── i18n/
        ├── request.ts       # Обработка i18n запросов.
        └── routing.ts       # Логика маршрутов для локализации. [Документация](https://nextjs.org/docs/app/building-your-application/optimizing/internationalization)

```


This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
