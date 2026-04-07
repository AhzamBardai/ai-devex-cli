export interface Product {
  id: string;
  name: string;
  priceUsd: number;
  stock: number;
}

export interface Order {
  id: string;
  customerId: string;
  items: Array<{ productId: string; quantity: number }>;
  totalUsd: number;
  status: 'pending' | 'placed' | 'shipped' | 'delivered';
}
