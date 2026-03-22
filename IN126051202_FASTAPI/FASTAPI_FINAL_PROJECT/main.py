## I AM SEJALSINHA AND I HAVE CHOOSE FASHION STORE 

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Casual Shirt", "brand": "Zara", "category": "Shirt", "price": 1200, "sizes_available": ["S", "M", "L"], "in_stock": True},
    {"id": 2, "name": "Denim Jeans", "brand": "Levis", "category": "Jeans", "price": 2000, "sizes_available": ["M", "L"], "in_stock": True},
    {"id": 3, "name": "Running Shoes", "brand": "Nike", "category": "Shoes", "price": 3500, "sizes_available": ["8", "9", "10"], "in_stock": False},
    {"id": 4, "name": "Summer Dress", "brand": "H&M", "category": "Dress", "price": 1800, "sizes_available": ["S", "M"], "in_stock": True},
    {"id": 5, "name": "Winter Jacket", "brand": "Puma", "category": "Jacket", "price": 4000, "sizes_available": ["L", "XL"], "in_stock": True},
    {"id": 6, "name": "Formal Shirt", "brand": "Allen Solly", "category": "Shirt", "price": 1500, "sizes_available": ["M", "L"], "in_stock": True},
]

orders = []
wishlist = []
order_counter = 1

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    size: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0, le=10)
    delivery_address: str = Field(..., min_length=10)
    gift_wrap: bool = False
    season_sale: bool = False


class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    sizes_available: List[str]
    in_stock: bool = True



def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def calculate_order_total(price, quantity, gift_wrap, season_sale):
    base = price * quantity
    discount = 0
    bulk_discount = 0
    gift_cost = 0

    if season_sale:
        discount = 0.15 * base
        base -= discount

    if quantity >= 5:
        bulk_discount = 0.05 * base
        base -= bulk_discount

    if gift_wrap:
        gift_cost = 50 * quantity
        base += gift_cost

    return {
        "final_total": int(base),
        "season_discount": int(discount),
        "bulk_discount": int(bulk_discount),
        "gift_wrap_cost": gift_cost
    }


def filter_products_logic(category, brand, max_price, in_stock):
    result = products

    if category is not None:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if brand is not None:
        result = [p for p in result if p["brand"].lower() == brand.lower()]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return result


@app.get("/")
def home():
    return {"message": "Welcome to TrendZone Fashion Store"}


@app.get("/products")
def get_products():
    total = len(products)
    in_stock_count = len([p for p in products if p["in_stock"]])
    return {"products": products, "total": total, "in_stock_count": in_stock_count}


@app.get("/products/summary")
def product_summary():
    brands = list(set([p["brand"] for p in products]))
    categories = {}

    for p in products:
        categories[p["category"]] = categories.get(p["category"], 0) + 1

    return {
        "total": len(products),
        "in_stock": len([p for p in products if p["in_stock"]]),
        "out_of_stock": len([p for p in products if not p["in_stock"]]),
        "brands": brands,
        "category_count": categories
    }


@app.get("/orders")
def get_orders():
    total_revenue = sum([o["total"] for o in orders])
    return {"orders": orders, "total": len(orders), "total_revenue": total_revenue}


@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    max_price: Optional[int] = None,
    in_stock: Optional[bool] = None
):
    result = filter_products_logic(category, brand, max_price, in_stock)
    return {"results": result, "count": len(result)}



@app.get("/products/search")
def search_products(keyword: str):
    result = [
        p for p in products
        if keyword.lower() in p["name"].lower()
        or keyword.lower() in p["brand"].lower()
        or keyword.lower() in p["category"].lower()
    ]
    if not result:
        return {"message": "No products found"}
    return {"results": result, "total_found": len(result)}


@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    valid_fields = ["price", "name", "brand", "category"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    reverse = True if order == "desc" else False

    sorted_list = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {"sorted_by": sort_by, "order": order, "results": sorted_list}


@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 3):
    total = len(products)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "results": products[start:end]
    }



@app.post("/products", status_code=201)
def add_product(product: NewProduct):
    for p in products:
        if p["name"] == product.name and p["brand"] == product.brand:
            raise HTTPException(status_code=400, detail="Product already exists")

    new_product = product.dict()
    new_product["id"] = len(products) + 1
    products.append(new_product)
    return new_product


@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):
    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    global products

    for o in orders:
        if o["product_id"] == product_id:
            raise HTTPException(status_code=400, detail="Cannot delete product with orders")

    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    products = [p for p in products if p["id"] != product_id]

    return {"message": "Product deleted"}



@app.post("/orders")
def create_order(order: OrderRequest):
    global order_counter

    product = find_product(order.product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail="Product out of stock")

    if order.size not in product["sizes_available"]:
        raise HTTPException(status_code=400, detail=f"Available sizes: {product['sizes_available']}")

    calc = calculate_order_total(product["price"], order.quantity, order.gift_wrap, order.season_sale)

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "product_name": product["name"],
        "brand": product["brand"],
        "size": order.size,
        "quantity": order.quantity,
        "gift_wrap": order.gift_wrap,
        "total": calc["final_total"]
    }

    order_counter += 1
    orders.append(new_order)

    return {"order": new_order, "breakdown": calc}



@app.post("/wishlist/add")
def add_to_wishlist(customer_name: str, product_id: int, size: str):
    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if size not in product["sizes_available"]:
        raise HTTPException(status_code=400, detail="Invalid size")

    for item in wishlist:
        if item["customer_name"] == customer_name and item["product_id"] == product_id and item["size"] == size:
            raise HTTPException(status_code=400, detail="Already in wishlist")

    wishlist.append({
        "customer_name": customer_name,
        "product_id": product_id,
        "size": size,
        "price": product["price"]
    })

    return {"message": "Added to wishlist"}


@app.get("/wishlist")
def get_wishlist():
    total_value = sum([item["price"] for item in wishlist])
    return {"wishlist": wishlist, "total_value": total_value}


@app.delete("/wishlist/remove")
def remove_wishlist(customer_name: str, product_id: int):
    global wishlist
    wishlist = [w for w in wishlist if not (w["customer_name"] == customer_name and w["product_id"] == product_id)]
    return {"message": "Removed from wishlist"}


@app.post("/wishlist/order-all", status_code=201)
def order_all(customer_name: str, delivery_address: str):
    global wishlist, order_counter

    user_items = [w for w in wishlist if w["customer_name"] == customer_name]

    if not user_items:
        raise HTTPException(status_code=400, detail="Wishlist empty")

    confirmations = []
    grand_total = 0

    for item in user_items:
        product = find_product(item["product_id"])

        calc = calculate_order_total(product["price"], 1, False, False)

        new_order = {
            "order_id": order_counter,
            "customer_name": customer_name,
            "product_id": product["id"],
            "product_name": product["name"],
            "brand": product["brand"],
            "size": item["size"],
            "quantity": 1,
            "total": calc["final_total"]
        }

        orders.append(new_order)
        confirmations.append(new_order)
        grand_total += calc["final_total"]
        order_counter += 1

    wishlist = [w for w in wishlist if w["customer_name"] != customer_name]

    return {"orders": confirmations, "grand_total": grand_total}

@app.get("/orders/search")
def search_orders(customer_name: str):
    result = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    return {"results": result}


@app.get("/orders/sort")
def sort_orders(sort_by: str = "total"):
    return {"results": sorted(orders, key=lambda x: x.get(sort_by, 0))}


@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 2):
    total = len(orders)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {"page": page, "total_pages": total_pages, "results": orders[start:end]}



@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    in_stock: Optional[bool] = None,
    max_price: Optional[int] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = products

    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    result = filter_products_logic(category, brand, max_price, in_stock)

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x.get(sort_by, ""), reverse=reverse)

    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "results": result[start:end]
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product