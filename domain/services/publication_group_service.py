import math
import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances

from sqlalchemy import func

from infrastructure.database.models import (
    PublicationProfitabilityEntity,
    MeliPublicationEntity,
    PublicationSaleEntity,
)


class PublicationGroupService:
    def __init__(self, db):
        self.db = db

    def group_by_price_and_margin(self, max_per_group: int = 10):
        sales_subquery = (
            self.db.query(
                PublicationSaleEntity.publication_id.label("publication_id"),
                func.coalesce(func.sum(PublicationSaleEntity.quantity), 0).label("total_units_sold"),
                func.coalesce(func.sum(PublicationSaleEntity.total_amount), 0).label("total_sales_amount"),
                func.count(PublicationSaleEntity.id).label("total_orders"),
            )
            .group_by(PublicationSaleEntity.publication_id)
            .subquery()
        )

        records = (
            self.db.query(
                PublicationProfitabilityEntity,
                MeliPublicationEntity,
                sales_subquery.c.total_units_sold,
                sales_subquery.c.total_sales_amount,
                sales_subquery.c.total_orders,
            )
            .join(
                MeliPublicationEntity,
                MeliPublicationEntity.publication_id
                == PublicationProfitabilityEntity.publication_id,
            )
            .outerjoin(
                sales_subquery,
                sales_subquery.c.publication_id
                == MeliPublicationEntity.publication_id,
            )
            .all()
        )

        data = []

        for (
            profitability,
            publication,
            total_units_sold,
            total_sales_amount,
            total_orders,
        ) in records:
            margin = profitability.recommended_margin_percent
            profit = profitability.recommended_profit

            if profitability.price is None or margin is None:
                continue

            if float(profitability.price) <= 0:
                continue

            data.append({
                "publication_id": publication.publication_id,
                "title": publication.title,
                "thumbnail": publication.thumbnail,
                "permalink": publication.permalink,
                "price": float(profitability.price or 0),
                "margin": float(margin or 0),
                "profit": float(profit or 0),
                "recommended_cost_type": profitability.recommended_cost_type,

                # VENTAS
                "total_units_sold": int(total_units_sold or 0),
                "total_sales_amount": float(total_sales_amount or 0),
                "total_orders": int(total_orders or 0),
            })

        if not data:
            return {
                "total_publications": 0,
                "total_groups": 0,
                "groups": [],
            }

        df = pd.DataFrame(data)

        total = len(df)
        n_groups = math.ceil(total / max_per_group)

        X = df[["price", "margin"]].astype(float)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(
            n_clusters=n_groups,
            random_state=42,
            n_init=10,
        )

        kmeans.fit(X_scaled)

        distances = pairwise_distances(
            X_scaled,
            kmeans.cluster_centers_,
        )

        group_counts = {i: 0 for i in range(n_groups)}
        final_assignment = [None] * total

        closest_distance = distances.min(axis=1)
        order = np.argsort(-closest_distance)

        for idx in order:
            nearest_groups = np.argsort(distances[idx])

            for group_id in nearest_groups:
                if group_counts[group_id] < max_per_group:
                    final_assignment[idx] = int(group_id)
                    group_counts[group_id] += 1
                    break

        df["group_id"] = final_assignment

        groups = []

        for group_id, group_df in df.groupby("group_id"):
            group_df = group_df.sort_values(
                ["total_sales_amount", "price", "margin"],
                ascending=[False, True, True],
            )

            total_group_sales_amount = float(group_df["total_sales_amount"].sum())
            total_group_units_sold = int(group_df["total_units_sold"].sum())
            total_group_orders = int(group_df["total_orders"].sum())

            groups.append({
                "group_id": int(group_id),
                "total_publications": int(len(group_df)),

                "avg_price": float(group_df["price"].mean()),
                "min_price": float(group_df["price"].min()),
                "max_price": float(group_df["price"].max()),

                "avg_margin": float(group_df["margin"].mean()),
                "min_margin": float(group_df["margin"].min()),
                "max_margin": float(group_df["margin"].max()),

                # VENTAS DEL GRUPO
                "total_units_sold": total_group_units_sold,
                "total_sales_amount": total_group_sales_amount,
                "total_orders": total_group_orders,

                "publications": group_df.to_dict(orient="records"),
            })

        groups = sorted(
            groups,
            key=lambda group: group["group_id"],
        )

        return {
            "total_publications": total,
            "max_per_group": max_per_group,
            "total_groups": len(groups),
            "total_units_sold": int(df["total_units_sold"].sum()),
            "total_sales_amount": float(df["total_sales_amount"].sum()),
            "total_orders": int(df["total_orders"].sum()),
            "groups": groups,
        }