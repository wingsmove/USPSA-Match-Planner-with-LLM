import type { ReactNode } from "react";

export type TableColumn<T> = {
  key: string;
  header: ReactNode;
  render: (item: T) => ReactNode;
};

type DataTableProps<T> = {
  items: T[];
  columns: TableColumn<T>[];
  getRowKey: (item: T) => string | number;
  emptyMessage: string;
};

function DataTable<T>({
  items,
  columns,
  getRowKey,
  emptyMessage,
}: DataTableProps<T>) {
  if (items.length === 0) {
    return <p className="empty-state">{emptyMessage}</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={getRowKey(item)}>
              {columns.map((column) => (
                <td key={column.key}>{column.render(item)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
