/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,jsx,ts,tsx}",   // <-- this is the only change you need
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#1DB954',
                    dark: '#1aa34a',
                    light: '#1ed760',
                },
                dark: {
                    DEFAULT: '#121212',
                    lighter: '#181818',
                    card: '#282828',
                },
                gray: {
                    text: '#b3b3b3',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
};