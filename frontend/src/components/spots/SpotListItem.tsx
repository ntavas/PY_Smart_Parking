type Props = {
    name: string;
    address: string;
    pricePerHour: number;
    minutesWalk: number | null;
    showReserve: boolean;
    onNavigate?: () => void;
};

export default function SpotListItem({
    name,
    address,
    pricePerHour,
    minutesWalk,
    showReserve,
    onNavigate,
}: Props) {
    return (
        <div className="rounded-lg border border-gray-400 bg-white p-4 shadow-sm dark:border-gray-500 dark:bg-gray-800">
            <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                        {name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                        {address}
                    </p>
                    <div className="mt-2 flex items-center gap-4 text-sm">
                        <span className="text-green-600 dark:text-green-400 font-medium">
                            Free parking
                        </span>
                        {minutesWalk && (
                            <span className="text-gray-500 dark:text-gray-400">
                                {minutesWalk} min drive
                            </span>
                        )}
                    </div>
                </div>
                <div className="flex flex-col gap-2 ml-3">
                    {showReserve && (
                        <button
                            className="px-3 py-1.5 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                            disabled
                        >
                            Reserve
                        </button>
                    )}
                    <button
                        onClick={onNavigate}
                        className="px-3 py-1.5 text-sm rounded-md bg-green-600 text-white hover:bg-green-700 transition-colors"
                    >
                        Navigate
                    </button>
                </div>
            </div>
        </div>
    );
}
