'use client';

import Image from 'next/image';

export default function ProfileSettings() {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="min-h-screen flex flex-col items-center">
        <div className="grid grid-cols-1 md:grid-cols-7 gap-[30px] w-full">
          {/* Левая колонка (навигация) */}
          <div className="col-span-1 md:col-span-3 flex flex-col text-center md:text-left gap-6">
            <div className="flex flex-col gap-4">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4">Account Settings</h1>
              <button className="px-4 py-2 border border-black rounded-md hover:bg-gray-100 transition-colors text-base">
                Logout
              </button>
            </div>
            <nav className="space-y-2">
              <button className="w-full px-4 py-2 border border-black rounded-md hover:bg-gray-100 transition-colors text-base">
                Personal Information
              </button>
              <button className="w-full px-4 py-2 border border-black rounded-md hover:bg-gray-100 transition-colors text-base">
                Addresses
              </button>
              <button className="w-full px-4 py-2 border border-black rounded-md hover:bg-gray-100 transition-colors text-base">
                Security
              </button>
              <button className="w-full px-4 py-2 border border-black rounded-md hover:bg-gray-100 transition-colors text-base">
                Preferences
              </button>
              <a href="/profile/orders" className="w-full block px-4 py-2 border border-black rounded-md hover:bg-gray-100 transition-colors text-base text-center">
                Orders
              </a>
            </nav>
          </div>

          {/* Правая колонка (контент) */}
          <div className="col-span-1 md:col-span-4 flex flex-col gap-8">
            <div>
              <h2 className="text-2xl font-semibold mb-6">Personal Information</h2>

              {/* Аватар */}
              <div className="flex items-center gap-4 mb-6">
                <div className="relative w-20 h-20 rounded-full overflow-hidden bg-gray-200">
                  <Image
                    src="/default-avatar.png"
                    alt="Profile"
                    fill
                    className="object-cover"
                  />
                </div>
                <button className="px-4 py-2 border border-black rounded hover:bg-gray-100 transition-colors text-sm font-medium">
                  Change Photo
                </button>
              </div>

              {/* Форма персональных данных */}
              <form className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm mb-1">First Name</label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-black rounded focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm mb-1">Last Name</label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-black rounded focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm mb-1">Email</label>
                  <input
                    type="email"
                    className="w-full px-3 py-2 border border-black rounded focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm mb-1">Phone</label>
                  <input
                    type="tel"
                    className="w-full px-3 py-2 border border-black rounded focus:outline-none"
                  />
                </div>

                <button
                  type="button"
                  className="w-full bg-black text-white py-2 rounded hover:bg-gray-800 transition-colors"
                >
                  Save Changes
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
