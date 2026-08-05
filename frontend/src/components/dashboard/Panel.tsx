import type { ReactNode } from "react";

type Props = {
    title: string;
    subtitle?: string;
    eyebrow?: string;
    action?: ReactNode;
    children: ReactNode;
    className?: string;
    testId?: string;
};

export default function Panel({
    title,
    subtitle,
    eyebrow,
    action,
    children,
    className,
    testId,
}: Props) {

    return (
        <section className={`panel ${className ?? ""}`.trim()} data-testid={testId}>
            <header className="panel__header">
                <div>
                    {eyebrow ? <p className="panel__eyebrow">{eyebrow}</p> : null}
                    <h2 className="panel__title">{title}</h2>
                    {subtitle ? <p className="panel__subtitle">{subtitle}</p> : null}
                </div>
                {action ? <div className="panel__action">{action}</div> : null}
            </header>
            <div className="panel__body">{children}</div>
        </section>
    );
}