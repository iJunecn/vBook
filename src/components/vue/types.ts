export interface BookListItem {
  id: string;
  title: string;
  author: string | null;
  publisher: string | null;
  isbn: string | null;
  edition: string | null;
  price: string;
  status: string;
  sellerNickname: string | null;
  sellerCampus: string | null;
}

export const CAMPUS_LABELS: Record<string, string> = {
  main: '主校区',
  north: '北校区',
  south: '南校区',
  east: '东校区',
};
