from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

db = SQLAlchemy()
cache = Cache()

def get_reviews_by_city(city):
    from models.review import Review
    reviews = Review.query.filter_by(city=city).all()

    review_dict = {}

    for r in reviews:
        if r.place not in review_dict:
            review_dict[r.place] = {
                "reviews": [],
                "total_rating": 0,
                "count": 0
            }

        review_dict[r.place]["reviews"].append({
            "user": r.user_name,
            "rating": float(r.rating),
            "comment": r.comment
        })

        review_dict[r.place]["total_rating"] += float(r.rating)
        review_dict[r.place]["count"] += 1

    # Now calculate average
    for place in review_dict:
        total = review_dict[place]["total_rating"]
        count = review_dict[place]["count"]
        review_dict[place]["average"] = round(total / count, 1)

    return review_dict

def add_review(city, place, user_name, rating, comment):
    from models.review import Review
    new_review = Review(
        city=city,
        place=place,
        user_name=user_name,
        rating=int(rating),
        comment=comment
    )
    db.session.add(new_review)
    db.session.commit()