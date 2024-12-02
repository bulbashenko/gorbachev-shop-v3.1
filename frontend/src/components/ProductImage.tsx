import Image from 'next/image';
import { useState } from 'react';

interface ProductImageProps {
    src: string;
    alt: string;
    fill?: boolean;
    className?: string;
    priority?: boolean;
}

const ProductImage: React.FC<ProductImageProps> = ({
    src,
    alt,
    fill = true,
    className = '',
    priority = false
}) => {
    const [error, setError] = useState(false);

    const handleError = () => {
        setError(true);
    };

    // Более стильный SVG плейсхолдер
    const placeholderSvg = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23f3f4f6'/%3E%3Cpath d='M35 40h30v20H35z' fill='%23e5e7eb'/%3E%3Cpath d='M40 45h20v10H40z' fill='%23d1d5db'/%3E%3Ccircle cx='50' cy='50' r='15' stroke='%239ca3af' stroke-width='2' stroke-dasharray='4 2'/%3E%3Cpath d='M45 50h10M50 45v10' stroke='%239ca3af' stroke-width='2'/%3E%3C/svg%3E`;

    return (
        <Image
            src={error ? placeholderSvg : src}
            alt={alt}
            fill={fill}
            className={`object-cover ${className}`}
            onError={handleError}
            priority={priority}
            blurDataURL={placeholderSvg}
            placeholder="blur"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />
    );
};

export default ProductImage;