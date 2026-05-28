import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Media Compose Dashboard",
  description: "Dashboard de monitoramento para ilhas de edição",
};

const themeInitializerScript = `
  (function () {
    try {
      var storedTheme = localStorage.getItem("media-compose-theme");
      var prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      var shouldUseDark = storedTheme ? storedTheme === "dark" : prefersDark;
      var root = document.documentElement;
      root.classList.toggle("dark", shouldUseDark);
      root.style.colorScheme = shouldUseDark ? "dark" : "light";
    } catch (error) {
      document.documentElement.classList.remove("dark");
      document.documentElement.style.colorScheme = "light";
    }
  })();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitializerScript }} />
      </head>
      <body className="
          bg-slate-50 text-slate-900
          dark:bg-slate-950 dark:text-[rgba(227,227,233,1)]
          transition-colors duration-300
        "
      >{children}
      </body>
    </html>
  );
}
