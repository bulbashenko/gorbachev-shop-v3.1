// utils/navigationLinks.tsx
import { FaHome, FaUser, FaEnvelope, FaCog, FaInfoCircle, FaPhone } from 'react-icons/fa';

// Определяем тип для ссылки
interface LinkItem {
  href: string;
  labelKey: string;
  smallLabelKey: string;
  icon: JSX.Element; // Указываем, что icon должен быть JSX-элементом
}

const links: LinkItem[] = [
  { href: '/catalog', labelKey: 'allProducts', smallLabelKey: 'sm-allProducts', icon: <FaHome /> },
  { href: '/catalog/sweaters', labelKey: 'sweaters', smallLabelKey: 'sm-sweaters', icon: <FaUser /> },
  { href: '/catalog/pants', labelKey: 'pants', smallLabelKey: 'sm-pants', icon: <FaInfoCircle /> },
  { href: '/catalog/bags', labelKey: 'bags', smallLabelKey: 'sm-bags', icon: <FaPhone /> },
  { href: '/catalog/tshirts', labelKey: 'tshirts', smallLabelKey: 'sm-tshirts', icon: <FaEnvelope /> },
  { href: '/catalog/accessories', labelKey: 'accessories', smallLabelKey: 'sm-accessories', icon: <FaCog /> },
];

export default links;
