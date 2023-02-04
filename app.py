from flask import Flask, render_template, redirect, request, jsonify
import requests
import random


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
            elif site_name == "yummly.com":
                reviews = getReviewsYummlyDotCom(review_count)
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


def getReviewsYummlyDotCom(review_count):
    link = "https://mapi.yummly.com/mapi/v19/content/feed?start=0&limit=20&fetchUserCollections=false&allowedContent=single_recipe&allowedContent=suggested_search&allowedContent=related_search&allowedContent=article&allowedContent=video&allowedContent=generic_cta"
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
        feed_data = resp.get('feed')
        random.shuffle(feed_data)
        generated_reviews = []
    except:
        feed_data = []
    for data in feed_data:
        if data.get('content').get('reviews') is None:
            continue
        if data.get('content').get('reviews').get('totalReviewCount') == 0:
            continue
        product_id = data.get('content').get('details').get('globalId')
        link = "https://mapi.yummly.com/mapi/v19/recipe/{}/reviews?offset=0&limit={}".format(
            product_id, review_count)
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
            reviews = resp.get('reviews')[:review_count]

            for review in reviews:
                generated_reviews.append({
                    'rating': review.get('rating'),
                    'reviewed_by': review.get('user').get('displayName'),
                    'review_text': review.get('text')
                })
                if len(generated_reviews) == review_count:
                    break
        except:
            return []
        if len(generated_reviews) == review_count:
            break
    return generated_reviews


if __name__ == '__main__':
    app.run(port=5000)
