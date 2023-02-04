from flask import Flask, render_template, redirect, request, jsonify
import requests


review_ranges = [5, 10, 15, 20]
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate')
def generateReviews():
    if request.method == "GET":
        site_name = request.args.get('site')
        review_count = request.args.get('reviews')
        if review_count is not None and review_count != "" and int(review_count) in review_ranges:
            review_count = int(review_count)
            if site_name == "food.com":
                reviews = getReviewsFoodDotCom(review_count)
                if len(reviews) == 0:
                    return jsonify({"error": "No reviews found for this site or perhaps there were some errors!"})
                return jsonify({"site": site_name, "count": review_count, "reviews": reviews})
        else:
            review_count = 5
    else:
        return redirect('/')


def getReviewsFoodDotCom(review_count):
    link = "https://api.food.com/external/v1/feed/reviews?pn=1&size={}&blockGdpr=false&_=1675492673966".format(
        review_count)
    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }
    try:
        resp = requests.get(link, headers=headers).json()
    except:
        print("Failed to open {}".format(link))
        return []
    try:
        reviews = resp.get('data').get('items')[:review_count]
        generated_reviews = []
        for review in reviews:
            generated_reviews.append({
                'rating': review.get('rating'),
                'reviewed_by': review.get('memberName'),
                'review_text': review.get('text')
            })
        return generated_reviews
    except:
        return []


if __name__ == '__main__':
    app.run(port=5000)
