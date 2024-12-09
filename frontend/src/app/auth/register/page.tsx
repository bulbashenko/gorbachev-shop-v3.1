"use client";

import { useState } from "react";
import Button from '../../components/Button';
import { type RegisterData } from '@/app/api/services/auth.service';
import { useTranslations, useLocale } from "next-intl";
import { dm_mono, pt_mono } from '../../utils/fontConfig';
import { useAuth } from '@/contexts/AuthContext';

export default function RegisterPage() {
  const t = useTranslations();
  const locale = useLocale();
  const { register } = useAuth(); // Используем метод register из контекста
  const monoFont = locale === 'ru' || locale === 'en' ? pt_mono : dm_mono;

  // State variables for form inputs
  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    username: '',
    password: '',
    password2: '',
    first_name: '',
    last_name: '',
    terms_accepted: false,
    newsletter_subscription: false,
  });

  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Function to handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  // Function to handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (formData.password !== formData.password2) {
      setError("Passwords do not match!");
      setIsLoading(false);
      return;
    }

    if (!formData.terms_accepted) {
      setError("You must accept the terms to register.");
      setIsLoading(false);
      return;
    }

    try {
      await register(formData); // Используем метод из контекста
    } catch (error) {
      if (error instanceof Error && error.message.toLowerCase().includes("already exists")) {
        setError("Account already exists. Please login.");
        // Не обязательно сразу рутить, можно подождать или просто предложить линк на логин
      } else {
        setError(error instanceof Error ? error.message : "Registration failed. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="min-h-screen flex flex-col items-center">
        <div className="grid grid-cols-1 md:grid-cols-7 gap-[30px]">
          {/* Блок 1: REGISTER */}
          <div className="col-span-1 md:col-span-3 flex flex-col items-center md:items-start text-center md:text-left">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-8">REGISTER</h1>
            {error && (
              <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
                {error}
              </div>
            )}
            <form onSubmit={handleSubmit} className="w-full grid grid-cols-1 md:grid-cols-7 gap-6">
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Username*"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
                required
              />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder={t('auth.email')}
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
                required
              />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Password*"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
                required
              />
              <input
                type="password"
                name="password2"
                value={formData.password2}
                onChange={handleChange}
                placeholder="Confirm Password*"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
                required
              />
              <div className="col-span-1 md:col-span-6 flex flex-col items-center md:items-start gap-4">
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Registering..." : "Register"}
                </Button>
                <div className={`${monoFont.className} text-base md:text-md text-whitesmoke`}>
                  * Must be filled in
                </div>
              </div>
            </form>
          </div>

          {/* Блок 2: ADDITIONAL INFO */}
          <div className="col-span-1 md:col-span-4 flex flex-col items-center md:items-start text-center md:text-left">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">ADDITIONAL INFO</h2>
            <div className="w-full grid grid-cols-1 md:grid-cols-7 gap-6 mb-6">
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="First Name"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Last Name"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
            </div>
            <div className="flex flex-col items-start gap-4 mb-6">
              <div className="flex flex-row items-center gap-2">
                <input
                  type="checkbox"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleChange}
                  className="w-5 h-5"
                />
                <div className={`${monoFont.className} text-base md:text-md font-light`}>
                  I have read the <span className="underline">terms of the agreement</span> and agree to them
                </div>
              </div>
              <div className="flex flex-row items-center gap-2">
                <input
                  type="checkbox"
                  name="newsletter_subscription"
                  checked={formData.newsletter_subscription}
                  onChange={handleChange}
                  className="w-5 h-5"
                />
                <div className={`${monoFont.className} text-base md:text-md font-light`}>
                  I want to receive promotional offers, customized new arrivals, trends and promotions.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
