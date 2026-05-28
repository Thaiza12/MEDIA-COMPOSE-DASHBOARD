"use client";

import { useEffect, useState } from "react";

type HeaderProps = {
  atualizadoEm: string;
  statusSistema: string;
  onRefresh: () => void;
};

const THEME_STORAGE_KEY = "media-compose-theme";

const applyTheme = (useDarkMode: boolean) => {
  const html = document.documentElement;
  html.classList.toggle("dark", useDarkMode);
  html.style.colorScheme = useDarkMode ? "dark" : "light";
  localStorage.setItem(THEME_STORAGE_KEY, useDarkMode ? "dark" : "light");
};

const buttonBase = `
  inline-flex h-9 items-center justify-center gap-2
  rounded-xl border border-slate-200/80 dark:border-white/10
  bg-white/90 px-3 text-xs font-medium sm:px-4 sm:text-sm
  text-slate-700 dark:bg-slate-900/70 dark:text-slate-200
  shadow-sm backdrop-blur transition-all duration-200
  hover:bg-slate-50 hover:text-slate-900
  dark:hover:bg-slate-800/80 dark:hover:text-white
`;

const iconButton = `
  inline-flex h-9 w-9 items-center justify-center rounded-full
  border border-slate-200/80 dark:border-white/10
  bg-white/90 text-slate-500
  shadow-sm backdrop-blur transition-all duration-200
  hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900
  active:scale-95
  dark:bg-slate-900/70 dark:text-slate-300
  dark:hover:border-slate-600 dark:hover:bg-slate-800/80 dark:hover:text-white
`;

export default function Header({ atualizadoEm, statusSistema, onRefresh }: HeaderProps) {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isThemeReady, setIsThemeReady] = useState(false);

  useEffect(() => {
    setIsDarkMode(document.documentElement.classList.contains("dark"));
    setIsThemeReady(true);
  }, []);

  const toggleTheme = () => {
    if (!isThemeReady) return;

    setIsDarkMode((current) => {
      const next = !current;
      applyTheme(next);
      return next;
    });
  };

  return (
    <header className="flex flex-col gap-4 border-b border-slate-200 pb-5 dark:border-white/10 md:flex-row md:items-start md:justify-between">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          <h1 className="text-xl font-bold text-[rgba(30,30,30,1)] dark:text-[rgba(240,240,245,1)] sm:text-2xl">
            Media Compose Dashboard
          </h1>

          <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] text-emerald-500 dark:text-emerald-300 sm:px-3 sm:text-xs">
            {statusSistema}
          </span>
        </div>

        <p className="mt-1 text-xs text-[rgba(100,100,100,1)] dark:text-[rgba(160,160,170,1)] sm:text-sm">
          Monitoramento e Inteligencia para Ilhas de Edicao
        </p>
      </div>

      <div className="flex w-full flex-wrap items-center gap-2 md:w-auto md:justify-end md:gap-3">
        <span className="mr-auto text-xs text-[rgba(140,140,140,1)] dark:text-[rgba(140,140,150,1)] sm:text-sm md:mr-0">
          Atualizado: {atualizadoEm}
        </span>

        <button onClick={onRefresh} className={buttonBase} type="button">
          Atualizar
        </button>

        <button className={iconButton} type="button" aria-label="Notificacoes" title="Notificacoes">
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M14.86 17.27a2.99 2.99 0 0 1-5.72 0m8.7-2.27H6.16a1 1 0 0 1-.97-1.26l.34-1.18a2 2 0 0 0 .07-.55V9a6.4 6.4 0 0 1 12.8 0v3.01c0 .19.02.37.07.55l.34 1.18a1 1 0 0 1-.97 1.26Z"
            />
          </svg>
        </button>

        <button className={iconButton} type="button" aria-label="Configuracoes" title="Configuracoes">
          <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8">
            <circle cx="12" cy="12" r="3.2" />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12.22 2h-.44a2 2 0 0 0-1.96 1.61l-.2 1.03a7.98 7.98 0 0 0-1.76 1.02l-.97-.33a2 2 0 0 0-2.41.91l-.22.38a2 2 0 0 0 .28 2.32l.73.8a8.06 8.06 0 0 0 0 2.04l-.73.8a2 2 0 0 0-.28 2.32l.22.38a2 2 0 0 0 2.41.91l.97-.33a7.98 7.98 0 0 0 1.76 1.02l.2 1.03A2 2 0 0 0 11.78 22h.44a2 2 0 0 0 1.96-1.61l.2-1.03a7.98 7.98 0 0 0 1.76-1.02l.97.33a2 2 0 0 0 2.41-.91l.22-.38a2 2 0 0 0-.28-2.32l-.73-.8a8.06 8.06 0 0 0 0-2.04l.73-.8a2 2 0 0 0 .28-2.32l-.22-.38a2 2 0 0 0-2.41-.91l-.97.33a7.98 7.98 0 0 0-1.76-1.02l-.2-1.03A2 2 0 0 0 12.22 2z"
            />
          </svg>
        </button>

        <button
          type="button"
          role="switch"
          aria-checked={isDarkMode}
          aria-label={isDarkMode ? "Trocar para modo claro" : "Trocar para modo escuro"}
          title={isDarkMode ? "Modo escuro ativo" : "Modo claro ativo"}
          onClick={toggleTheme}
          disabled={!isThemeReady}
          className={`
            relative inline-flex h-8 w-[68px] items-center rounded-full border
            border-slate-200/80 bg-white/90 p-1 shadow-sm backdrop-blur
            transition-opacity duration-150 dark:border-white/10 dark:bg-slate-900/70
            ${isThemeReady ? "opacity-100" : "opacity-0"}
          `}
        >
          <span className="absolute left-2 text-slate-400 dark:text-slate-500" aria-hidden>
            <svg viewBox="0 0 24 24" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="1.8">
              <circle cx="12" cy="12" r="3.2" />
              <path strokeLinecap="round" d="M12 2.75v2.2M12 19.05v2.2M21.25 12h-2.2M4.95 12h-2.2M18.54 5.46l-1.56 1.56M7.02 16.98l-1.56 1.56M18.54 18.54l-1.56-1.56M7.02 7.02 5.46 5.46" />
            </svg>
          </span>

          <span className="absolute right-2 text-slate-400 dark:text-slate-500" aria-hidden>
            <svg viewBox="0 0 24 24" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79Z" />
            </svg>
          </span>

          <span
            className={`
              flex h-6 w-6 items-center justify-center rounded-full text-white
              bg-amber-500 shadow-sm ${isThemeReady ? "transition-transform duration-300" : ""}
              ${isDarkMode ? "translate-x-9 bg-slate-700" : "translate-x-0"}
            `}
            aria-hidden
          >
            {isDarkMode ? (
              <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79Z" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="1.8">
                <circle cx="12" cy="12" r="3.2" />
                <path strokeLinecap="round" d="M12 2.75v2.2M12 19.05v2.2M21.25 12h-2.2M4.95 12h-2.2M18.54 5.46l-1.56 1.56M7.02 16.98l-1.56 1.56M18.54 18.54l-1.56-1.56M7.02 7.02 5.46 5.46" />
              </svg>
            )}
          </span>
        </button>
      </div>
    </header>
  );
}
