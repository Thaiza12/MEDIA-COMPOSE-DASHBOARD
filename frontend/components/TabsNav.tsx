const tabs = ["Visao Geral", "Ilhas", "Analytics", "Historico"];

type Props = {
  active: number;
  onChange: (index: number) => void;
};

export default function TabsNav({ active, onChange }: Props) {
  return (
    <nav className="-mx-1 overflow-x-auto pb-1">
      <div className="flex min-w-max gap-2 px-1">
        {tabs.map((tab, index) => {
          const isActive = active === index;

          return (
            <button
              key={tab}
              onClick={() => onChange(index)}
              type="button"
              className={`
                whitespace-nowrap rounded-lg border px-3 py-2 text-sm font-medium transition sm:px-4
                ${isActive
                  ? "border-transparent bg-[rgba(49,77,117,1)] text-[rgba(227,227,233,1)]"
                  : "border-[rgba(0,0,0,0.1)] bg-[rgba(255,255,255,1)] text-[rgba(30,30,30,1)] hover:bg-[rgba(235,235,235,1)] dark:border-white/10 dark:bg-[rgba(37,37,37,1)] dark:text-[rgba(200,200,210,1)] dark:hover:bg-[rgba(50,50,50,1)]"
                }
              `}
            >
              {tab}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
