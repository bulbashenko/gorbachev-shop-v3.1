// navigationLinks.tsx

import { ReactNode } from 'react';
import { FaBoxOpen, FaTshirt, FaShoppingBag, FaGem } from 'react-icons/fa';
import { PiPants } from 'react-icons/pi'

export interface NavigationLink {
  href: string;
  labelKey: string;
  mobLabelKey: string;
  icon: ReactNode;
}

const navigationLinks: NavigationLink[] = [
  {
    href: '/all-products',
    labelKey: 'navigation.allProducts',
    mobLabelKey: 'navigation.mobAllProducts',
    icon: <FaBoxOpen />,
  },
  {
    href: '/sweaters',
    labelKey: 'navigation.sweaters',
    mobLabelKey: 'navigation.mobSweaters',
    icon: <FaTshirt />,
  },
  {
    href: '/pants',
    labelKey: 'navigation.pants',
    mobLabelKey: 'navigation.mobPants',
    icon: <PiPants />,
  },
  {
    href: '/bags',
    labelKey: 'navigation.bags',
    mobLabelKey: 'navigation.mobBags',
    icon: <FaShoppingBag />,
  },
  {
    href: '/t-shirts',
    labelKey: 'navigation.tshirts',
    mobLabelKey: 'navigation.mobTshirts',
    icon: <FaTshirt />,
  },
  {
    href: '/accessories',
    labelKey: 'navigation.accessories',
    mobLabelKey: 'navigation.mobAccessories',
    icon: <FaGem />,
  },
];

export default navigationLinks;
