import Image from 'next/image';
import { useState } from 'react';

interface ProductImageProps {
    src?: string | null;
    alt: string;
    priority?: boolean;
    fallback?: string;
}

export default function ProductImage({ 
    src, 
    alt, 
    priority = false,
    fallback = '/images/placeholder.jpg' 
}: ProductImageProps) {
    const [error, setError] = useState(false);
    
    const imageSrc = error || !src ? fallback : src;

    return (
        <Image
            src={imageSrc}
            alt={alt}
            fill
            className="object-cover"
            priority={priority}
            onError={() => setError(true)}
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />
    );
}