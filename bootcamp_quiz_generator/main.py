from fastapi import FastAPI
from database import quiz_collection, ai_quiz_collection
from bson import ObjectId
import json
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


app = FastAPI()


@app.get("/")
def get_quiz():
    quizzes = list(quiz_collection.find())

    for q in quizzes:
        q["_id"] = str(q["_id"])
        q["teacher"] = str(q["teacher"])

    return quizzes



@app.get("/get_quiz/{id}")
def get_quiz(id: str):
    quiz = quiz_collection.find_one({"_id": ObjectId(id)})

    if quiz:
        quiz["_id"] = str(quiz["_id"])
        quiz["teacher"] = str(quiz["teacher"])

    return quiz




def generate_quiz(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a quiz generator. Return ONLY valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    raw_output = response.choices[0].message.content

    # 🔥 IMPORTANT LINE
    parsed_output = json.loads(raw_output)

    return parsed_output


@app.post("/create_quiz/{id}")
def create_quiz(id: str):
    quiz = quiz_collection.find_one({"_id":ObjectId(id)})
    if not quiz:
        return {"error": "Quiz not found"}

    else:

        quiz["_id"] = str(quiz["_id"])
        quiz["teacher"] = str(quiz["teacher"])



    input_data= {   "quiz_id": quiz["_id"],
    "teacher_id": quiz["teacher"],
    "quiz_domain": quiz["domain"],
    "quiz_topics": quiz["topics"],
    "quiz_difficulty": quiz["difficulty"],
    "no_of_mcqs": quiz["numberOfQuestions"],
    }

    prompt = f"""
hello you are a ai mcqs generator teachers 

your role :
your role is to just follow my instructions properly dont add any text etc by yourself
you just have to return the json response

output structure :

response = {{
quiz_id:{quiz["_id"]},
teacher_id:{quiz["teacher"]},
mcqs:[
{{question:"",options:{{option_a:"",option_b:"",option_c:"",option_d:""}},correct_option:""}},
{{question:"",options:{{option_a:"",option_b:"",option_c:"",option_d:""}},correct_option:""}}
....... till the number of mcqs
]
no_of_mcqs:{quiz["numberOfQuestions"]}
}}

strict rules to follow:
You must return ONLY valid JSON. Use double quotes for keys and values. No extra text
i just want you to give me the mcq question there 4 options and correct answer till the number of mcqs i will provide
dont add any single extra text even not a single comma
you have to strictly follow this
you will just generate the mcqs related to the data i will provide in a cleanable json format
the questions should be related to the domain and topics {quiz["domain"]} and {quiz["topics"]}
 and the difficulty level should be {quiz["difficulty"]}

 additional rule:
If the response is not valid JSON, you must regenerate it again until it becomes valid JSON.
No exceptions.

""" 


    data=generate_quiz(prompt)


    ai_quiz_collection.insert_one({
        "quiz_id": quiz["_id"],
        "mcqs": data["mcqs"],
        "no_of_mcqs": data["no_of_mcqs"]
    })

    return {
        "mcqs": data["mcqs"],
        "no_of_mcqs": data["no_of_mcqs"]
    }


    
