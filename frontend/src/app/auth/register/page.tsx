'use client';

import { useLocale } from "next-intl";
import { dm_mono, pt_mono } from '../../utils/fontConfig';
import Button from '../../components/Button';

export default function RegisterPage() {
  const locale = useLocale();
  const monoFont = locale === 'ru' || locale === 'en' ? pt_mono : dm_mono;

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="min-h-screen flex flex-col items-center">
        <div className="grid grid-cols-1 md:grid-cols-7 gap-[30px]">
          {/* Блок 1: REGISTER */}
          <div className="col-span-1 md:col-span-3 flex flex-col items-center md:items-start text-center md:text-left">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-8">REGISTER</h1>
            <form className="w-full grid grid-cols-1 md:grid-cols-7 gap-6">
              <input
                type="text"
                placeholder="Username*"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
              <input
                type="email"
                placeholder="Email*"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
              <input
                type="password"
                placeholder="Password*"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
              <input
                type="password"
                placeholder="Confirm Password*"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
              <div className="col-span-1 md:col-span-6 flex flex-col items-center md:items-start gap-4">
                <Button>Register</Button>
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
                placeholder="First Name"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
              <input
                type="text"
                placeholder="Last Name"
                className={`${monoFont.className} col-span-1 md:col-span-6 px-4 py-3 border border-[#030303] dark:border-[#ededed] rounded-[6px] bg-transparent focus:outline-none placeholder-[#030303] dark:placeholder-[#ededed]`}
              />
            </div>
            <div className="flex flex-col items-start gap-4 mb-6">
              <div className="flex flex-row items-center gap-2">
                <input type="checkbox" className="w-5 h-5" />
                <div className={`${monoFont.className} text-base md:text-md font-light`}>
                  I have read the <span className="underline">terms of the agreement</span> and agree to them
                </div>
              </div>
              <div className="flex flex-row items-center gap-2">
                <input type="checkbox" className="w-5 h-5" />
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
