type SelectorOption = {
    value: string;
    label?: string;
};

type Props = {
    label: string;
    value: string;
    options: SelectorOption[];
    onChange: (value: string) => void;
    disabled?: boolean;
    testId?: string;
};

export default function SelectorField({
    label,
    value,
    options,
    onChange,
    disabled = false,
    testId,
}: Props) {
    return (
        <label className="selector-field" data-testid={testId}>
            <span className="selector-field__label">{label}</span>
            <select
                className="selector-field__control"
                value={value}
                onChange={(event) => onChange(event.target.value)}
                disabled={disabled}
            >
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label ?? option.value}
                    </option>
                ))}
            </select>
        </label>
    );
}
