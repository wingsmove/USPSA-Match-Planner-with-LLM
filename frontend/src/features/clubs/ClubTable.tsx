import DataTable, {
  type TableColumn,
} from "../../components/ui/DataTable";
import type { Club } from "./types";

type ClubTableProps = {
  clubs: Club[];
  onDelete: (id: number) => Promise<void>;
};

function ClubTable({ clubs, onDelete }: ClubTableProps) {
  const columns: TableColumn<Club>[] = [
    { key: "name", header: "俱乐部名称", render: (club) => club.club_name },
    {
      key: "url",
      header: "俱乐部网址",
      render: (club) => club.club_url,
    },
    {
      key: "actions",
      header: "",
      render: (club) => (
        <button
          type="button"
          onClick={() => void onDelete(club.id)}
          className="delete-button"
        >
          删除
        </button>
      ),
    },
  ];

  return (
    <DataTable
      items={clubs}
      columns={columns}
      getRowKey={(club) => club.id}
      emptyMessage="暂无俱乐部，先在上方新增一条吧。"
    />
  );
}

export default ClubTable;
