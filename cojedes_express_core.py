import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class OrderBreakdown:
    business_name: str
    product_name: str
    quantity: int
    bcv_rate: float
    subtotal_usd: float
    delivery_fee_usd: float
    driver_share_usd: float
    platform_share_usd: float
    total_usd: float
    subtotal_ves: float
    delivery_fee_ves: float
    driver_share_ves: float
    platform_share_ves: float
    total_ves: float


class CojedesExpressEngine:
    def __init__(self, seed_path: str = "seed_cojedes_express.json") -> None:
        self.seed_path = Path(seed_path)
        self.data: Dict[str, Any] = self._load_seed()
        self.delivery_total_usd: float = float(self.data["delivery_fee"]["total_usd"])
        self.driver_share_usd: float = float(self.data["delivery_fee"]["driver_usd"])
        self.platform_share_usd: float = float(self.data["delivery_fee"]["platform_usd"])

    def _load_seed(self) -> Dict[str, Any]:
        with self.seed_path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)

    def get_business(self, business_id: str) -> Optional[Dict[str, Any]]:
        for biz in self.data.get("businesses", []):
            if biz.get("id") == business_id:
                return biz
        return None

    def calculate_order(
        self,
        business_id: str,
        product_id: str,
        quantity: int,
        bcv_rate: float,
    ) -> OrderBreakdown:
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0.")
        if bcv_rate <= 0:
            raise ValueError("La tasa BCV debe ser mayor a 0.")

        biz = self.get_business(business_id)
        if not biz:
            raise ValueError(f"Comercio no encontrado: {business_id}")
        if biz.get("status") != "active":
            raise ValueError(f"El comercio '{biz.get('name')}' no está activo (estado: {biz.get('status')}).")

        product = next((p for p in biz.get("products", []) if p.get("id") == product_id and p.get("active")), None)
        if not product:
            raise ValueError(f"Producto activo no encontrado: {product_id}")

        unit_price_usd = float(product["price_usd"])
        subtotal_usd = round(unit_price_usd * quantity, 2)
        total_usd = round(subtotal_usd + self.delivery_total_usd, 2)

        return OrderBreakdown(
            business_name=biz["name"],
            product_name=product["name"],
            quantity=quantity,
            bcv_rate=bcv_rate,
            subtotal_usd=subtotal_usd,
            delivery_fee_usd=self.delivery_total_usd,
            driver_share_usd=self.driver_share_usd,
            platform_share_usd=self.platform_share_usd,
            total_usd=total_usd,
            subtotal_ves=round(subtotal_usd * bcv_rate, 2),
            delivery_fee_ves=round(self.delivery_total_usd * bcv_rate, 2),
            driver_share_ves=round(self.driver_share_usd * bcv_rate, 2),
            platform_share_ves=round(self.platform_share_usd * bcv_rate, 2),
            total_ves=round(total_usd * bcv_rate, 2),
        )


if __name__ == "__main__":
    engine = CojedesExpressEngine()
    tasa_bcv_prueba = 45.00
    resumen = engine.calculate_order(
        business_id="hamburguesas-gourmet",
        product_id="hg-01",
        quantity=1,
        bcv_rate=tasa_bcv_prueba,
    )
    print(f"Comercio: {resumen.business_name} | Producto: {resumen.product_name} x{resumen.quantity}")
    print(f"Tasa BCV: {resumen.bcv_rate:.2f} Bs/USD")
    print(f"Subtotal comercio:  (Bs. {resumen.subtotal_ves:.2f})")
    print(f"Envío total:  -> Repartidor:  | Plataforma: ")
    print(f"Total a cobrar al cliente:  (Bs. {resumen.total_ves:.2f})")
