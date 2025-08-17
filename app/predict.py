from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import numpy as np
import tensorflow as tf

from flask_login import login_required, current_user
from keras.preprocessing import image

predict_bp = Blueprint('predict', __name__)

# === Config ===
UPLOAD_FOLDER = 'app/static/uploads/'
MODEL_PATH = 'E:/vproject/vitamin_model_best.h5'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# === Load Model ===
model = tf.keras.models.load_model(MODEL_PATH)

# === Labels and Descriptions ===
class_labels = ["Vitamin A", "Vitamin B", "Vitamin C", "Vitamin D", "Vitamin E"]
vitamin_descriptions = {
    "Vitamin A": {
         "paragraph":"Helps with Dry skin,vision (e.g., night blindness), immune function, skin health, and weak immunity.Supports vision, skin, and immune health.",
         "bullets": [
 "Deficiency may lead to night blindness and dry eyes.",
 "Causes dry, face acne, rough skin and increases infection risk."
 ],

"note":"Consult a doctor or nutritionist for proper diagnosis, as similar symptoms can arise from other deficiencies."
    },


    "Vitamin B": {
         "paragraph":"Vitamin B refers to a group of B-complex vitamins including B1, B2, B3, B5, B6, B7, B9, and B12. These vitamins are essential for energy production, brain function, red blood cell formation, and cell metabolism. Deficiencies in different B vitamins can cause symptoms like fatigue, nerve issues, mouth sores, and memory problems.",
         "bullets": [
 "Deficiency may cause fatigue, irritability, and poor memory.",
 "Can lead to anemia, mouth sores, and nerve damage."
  ],

 "note":"Consult a doctor or nutritionist, as these symptoms may overlap with other conditions or deficiencies."
    },

    
 "Vitamin C": {
    "paragraph": "Deficiency can cause scurvy, bleeding gums, and weak immunity.A common symptom is frequent bruising or slow wound healing.Supports immunity, skin repair, and iron absorption.Boosts the immune system and improves skin health.",
    "bullets": [
        "Deficiency may lead to bleeding gums and frequent infections.",
        "Can cause dry skin, joint pain, and delayed wound healing."
    ],
    "note": "Seek medical advice for accurate evaluation, as multiple deficiencies can cause similar issues."
},
        

    
    "Vitamin D": {
          "paragraph": "Supports bone health and immune function. Deficiency may lead to weak bones, fatigue,frequent illness and depression. Essential for bone strength and immune support. Helps maintain strong muscles and overall wellness.",
           "bullets": [
"Deficiency may cause weak bones, fatigue, and back pain.",
"Can lead to depression, muscle aches, and poor immunity."
           ],

"note":"Consult a healthcare provider for confirmation, as other factors may contribute to these symptoms."
    },

    "Vitamin E": {
        "paragraph":"Protects cells from damage and supports immunity.Deficiency may lead to nerve damage, muscle weakness, and in some cases, hair thinning or hair loss due to poor scalp circulation.Protects cells, skin, and vision from oxidative damage.",
          "bullets": [
"Deficiency may result in muscle weakness and vision issues.",
"Can cause dry skin, poor coordination, and immune problems."
          ],
"note":"Please consult a doctor to rule out other potential causes of these symptoms."
},
}
# === Helpers ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Routes ===
@predict_bp.route('/upload', methods=['GET'])
def show_upload_form():
    return render_template('upload.html')

@predict_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        flash('No image uploaded!')
        return redirect(url_for('predict.show_upload_form'))

    file = request.files['image']

    if file.filename == '':
        flash('No selected file.')
        return redirect(url_for('predict.show_upload_form'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        return redirect(url_for('predict.predict_image', filename=filename))
    else:
        flash("Invalid file type.")
        return redirect(url_for('predict.show_upload_form'))

@predict_bp.route('/predict/<filename>')
@login_required
def predict_image(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Load and preprocess the image
    img = image.load_img(filepath, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # Run prediction
    prediction = model.predict(img_array)
    predicted_index = np.argmax(prediction)
    predicted_vitamin = class_labels[predicted_index]
    description = vitamin_descriptions.get(predicted_vitamin, "No description available.")

      # === Save prediction to MySQL ===
    import mysql.connector
    from datetime import datetime

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1231",
        database="userdb"
    )
    cursor = conn.cursor()

    
    # ✅ First: Get user_id using email
    cursor.execute("SELECT id FROM users1 WHERE email = %s", (current_user.email,))
    user_row = cursor.fetchone()
    user_id = user_row[0] if user_row else None

    # ✅ Second: Insert prediction into predictions table
    if user_id:
        insert_query = """
            INSERT INTO predictions (user_id, image_filename, prediction_result, predicted_at, vitamin)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            user_id,
            filename,
            predicted_vitamin,
            datetime.now(),
            predicted_vitamin
        ))

    # ✅ Third: Update the user's predicted_class
    update_query = "UPDATE users1 SET predicted_class = %s WHERE email = %s"
    cursor.execute(update_query, (predicted_vitamin, current_user.email))

    conn.commit()
    cursor.close()
    conn.close()

    return render_template(
        'result.html',
        uploaded_img='uploads/' + filename,
        prediction_result=predicted_vitamin,
        description=description,
        predicted_vitamin=predicted_vitamin  
    )


@predict_bp.route('/history')
@login_required
def history():
    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1231",
        database="userdb"
    )
    cursor = conn.cursor()

    # Get current user's ID from the users1 table
    cursor.execute("SELECT id FROM users1 WHERE email = %s", (current_user.email,))
    user_row = cursor.fetchone()

    if not user_row:
        cursor.close()
        conn.close()
        return render_template('history.html', predictions=[])

    user_id = user_row[0]

    # Fetch all predictions for the current user
    query = """
       SELECT image_filename, prediction_result, predicted_at, vitamin  
        FROM predictions 
        WHERE user_id = %s 
        ORDER BY predicted_at DESC
    """
    cursor.execute(query, (user_id,))
    predictions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('history.html', predictions=predictions)


@predict_bp.route('/remedies/<vitamin>')
@login_required
def remedies(vitamin):
    remedies_data = {
        'Vitamin A': {
            'symptoms': 'Poor night vision, dry skin, delayed wound healing, frequent infections.',
            'foods': 'Carrots, sweet potatoes, spinach, liver, dairy products.',
            'tips': ''' Eat orange and yellow fruits/vegetables rich in beta-carotene (carrots, sweet potatoes, pumpkin, mangoes)
                     Include leafy greens like spinach, kale, and amaranth
                     Add animal-based sources like eggs, liver, and whole milk to the diet
                    Cook veggies lightly with a little fat (like coconut or olive oil) to improve vitamin A absorption''',
            'note': '''Hair loss and dry, flaky skin could also be signs of vitamin A deficiency.
Consult a doctor for appropriate dosage and to rule out other nutritional causes.'''
},
       'Vitamin B': {
    'symptoms': 'Weakness, mouth sores, tingling hands/feet, fatigue, memory loss, mood swings.',
    'foods': 'Fish, red meat, dairy, eggs, fortified cereals.',
    'tips': '''Vegetarians may need supplements or fortified foods.
               Eat whole grains like brown rice, oats, and millets.
               Add legumes, lentils, and pulses regularly.
               Include leafy greens, bananas, and nuts (especially for B6).
               Add animal-based foods like dairy, fish, and eggs for B12 (or supplements if vegetarian).
              Fermented foods like curd and idli-dosa batter can support B-vitamin production.''',

     'note': '''If you’re experiencing hair thinning, numbness, or mood swings, this could relate to B vitamin deficiency.
Always consult a doctor before supplementing, as each B-vitamin has different requirements.'''
    },

     'Vitamin C': {
    'symptoms': 'Scurvy, bleeding gums, slow wound healing, fatigue, frequent colds, frequent infections.',
    'foods': 'Oranges, strawberries, kiwi, bell peppers, broccoli.',
    'tips': '''Eat raw fruits and veggies — vitamin C can be destroyed by heat.
               Eat citrus fruits like oranges, lemons, and sweet lime.
               Include guava, kiwi, strawberries, papaya, and amla (Indian gooseberry).
               Add green vegetables like bell peppers, broccoli, and cabbage.
              Drink fresh juices (without added sugar) for better absorption.''',

             'note': '''Gum bleeding, loose teeth, and skin rashes can all stem from vitamin C deficiency.
Consult a doctor if symptoms persist, especially if wounds heal slowly or you feel tired often.'''
 },


        'Vitamin D': {
            'symptoms': 'Bone pain, muscle weakness, fatigue, mood changes, frequent colds, hair fall,depression.',
            'foods': 'Fatty fish (salmon, sardines), egg yolks, fortified milk.',
            'tips': '''Expose your skin to sunlight 15–20 mins, 3–4 days/week).
                      Eat fatty fish like salmon, sardines, or mackerel.
                      Include egg yolks and fortified foods (like milk or cereals).
                      Consume mushrooms exposed to sunlight.
                      Exercise regularly to boost absorption and bone strength.''',
 'note': '''Hair fall, bone aches, and low energy may all be signs of vitamin D deficiency.
Consult a healthcare provider before taking supplements, especially for long-term correction.'''
 },

        'Vitamin E': {
            'symptoms': 'Muscle weakness, vision problems, immune issues, coordination issues,hair thinning',
            'foods': 'Almonds, sunflower seeds, spinach, avocados.',
            'tips': '''Include healthy fats to absorb Vitamin E efficiently.',
                    Add nuts and seeds like almonds, sunflower seeds, and peanuts.
                     Use cold-pressed vegetable oils like sunflower, wheat germ, or olive oil.
                     Include green leafy vegetables like spinach and broccoli.
                     Snack on avocados and include whole grains.''',

            'note': '''If you notice dry skin, brittle hair, or vision problems, vitamin E might be lacking.
It’s important to consult a doctor for proper evaluation and safe supplementation.'''
    },
}
    image_filename = request.args.get('image_filename')  # get image filename from URL
    info = remedies_data.get(vitamin, {
        'symptoms': 'N/A',
        'foods': 'N/A',
        'tips': 'No data available.',
    })
     # Ensure 'tips' is a valid string, and split by newline
    tips_list = info['tips'].split('\n') if isinstance(info['tips'], str) else []
    print(tips_list)  # Check if it's split correctly
  

    return render_template(
        'remedies.html',
        vitamin=vitamin,
        symptoms=info['symptoms'],
        foods=info['foods'],
        tips_list=tips_list,# Pass the tips as a list to the template
        note=info.get('note', ''),  
        remedies=remedies_data,
        image_filename=request.args.get('image_filename')  # this is passed from result page
    )

@predict_bp.route('/quiz', methods=['POST'])
def quiz():
    user_answer = request.form.get('vitamin')
    correct_answer = 'Vitamin D'

    if user_answer == correct_answer:
        flash('✅ Correct! Vitamin D is essential for strong bones and a healthy immune system.', 'success')
    else:
        flash('❌ Oops! Not quite. The correct answer is Vitamin D.', 'danger')

    return redirect(url_for('predict.educational'))

@predict_bp.route('/educational')
def educational():
    return render_template('educational.html'
                           )
