from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


class Order(BaseModel):
    customer_name: str
    product_name: str
    quantity: int


products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": True},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

orders = []


@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(results),
        "products": results
    }

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order: str = Query("asc")
):

    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = (order == "desc")

    sorted_products = sorted(
        products,
        key=lambda p: p[sort_by],
        reverse=reverse
    )

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }


@app.get("/products/page")
def paginate_products(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1)
):

    start = (page - 1) * limit
    paginated = products[start:start + limit]

    total_pages = -(-len(products) // limit)

    return {
        "page": page,
        "limit": limit,
        "total_products": len(products),
        "total_pages": total_pages,
        "products": paginated
    }



@app.post("/orders")
def create_order(order: Order):
    order_id = len(orders) + 1

    new_order = {
        "order_id": order_id,
        "customer_name": order.customer_name,
        "product_name": order.product_name,
        "quantity": order.quantity
    }

    orders.append(new_order)

    return {"message": "Order placed", "order": new_order}



@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):

    results = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not results:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(results),
        "orders": results
    }



@app.get("/products/sort-by-category")
def sort_by_category():

    result = sorted(
        products,
        key=lambda p: (p["category"], p["price"])
    )

    return {
        "products": result,
        "total": len(result)
    }



@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = Query(None),
    sort_by: str = Query("price"),
    order: str = Query("asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1)
):

    result = products

    # Search
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    # Sort
    if sort_by in ["price", "name"]:
        result = sorted(
            result,
            key=lambda p: p[sort_by],
            reverse=(order == "desc")
        )

    # Pagination
    total = len(result)
    start = (page - 1) * limit
    paginated = result[start:start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products": paginated
    }



@app.get("/orders/page")
def paginate_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1)
):

    start = (page - 1) * limit

    return {
        "page": page,
        "limit": limit,
        "total_orders": len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders": orders[start:start + limit]
    }



@app.get("/products/{product_id}")
def get_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            return p

    raise HTTPException(status_code=404, detail="Product not found")