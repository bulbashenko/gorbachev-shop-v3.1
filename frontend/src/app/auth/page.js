// src/app/auth/page.tsx
'use client';

import React from 'react';
import Button from '../components/Button';
import Link from 'next/link';

export default function AuthPage() {
  return (
    <div className="container mx-auto my-9 px-6 py-4">
      <div className="min-h-screen">
        <div className="grid grid-cols-1 md:grid-cols-7 gap-[30px]">
          {/* Блок 1: LOG IN */}
          <div className="col-span-1 md:col-span-3 flex flex-col">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-8">LOG IN</h1>
            <form className="w-full grid grid-cols-1 md:grid-cols-7 gap-6">
              <input
                type="email"
                placeholder="Email"
                className="col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none focus:border-gray-300 placeholder-[#030303] dark:placeholder-[#ededed]"
              />
              <input
                type="password"
                placeholder="Password"
                className="col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none focus:border-gray-300 placeholder-[#030303] dark:placeholder-[#ededed]"
              />
              <div className="col-span-1 md:col-span-6 flex flex-col items-start gap-4">
                <Link href="/forgot-password" className="text-base md:text-lg underline">
                  Forgot your password?
                </Link>
                <Button type="submit">Sign In</Button>
              </div>
            </form>
          </div>

          {/* Блок 2: NEW CUSTOMERS */}
          <div className="col-span-1 md:col-span-4 flex flex-col">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">NEW CUSTOMERS</h2>
            <p className="text-base md:text-lg lg:text-xl mb-8">
              Sign up for early Sale access plus tailored new arrivals, trends and promotions. To opt
              out, click unsubscribe in our emails.
            </p>
            <Link href="/register">
              <Button>Register</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
