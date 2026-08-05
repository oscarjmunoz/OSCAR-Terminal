type Props = {
    title: string;
    description: string;
};

export default function EmptyState({ title, description }: Props) {

    return (
        <div className="empty-state">
            <strong className="empty-state__title">{title}</strong>
            <p className="empty-state__description">{description}</p>
        </div>
    );
}