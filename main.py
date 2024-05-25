from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import streamlit as st
import os

openai_api_key = os.getenv('OPENAI_API_KEY')
# Windows
# set OPENAI_API_KEY=your_openai_api_key_here
# Linux
# export OPENAI_API_KEY=your_openai_api_key_here
# ??
# setx OPENAI_API_KEY api_key

generate_question_template = """
Wygeneruj unikalne pytanie quizowe dla {subject} z czterema możliwymi odpowiedziami, gdzie tylko jedna odpowiedź jest poprawna. Podaj poprawną odpowiedź oraz trzy niepoprawne odpowiedzi.
Sformatuj odpowiedź w następujący sposób:
Pytanie: [treść pytania]
A: [opcja 1]
B: [opcja 2]
C: [opcja 3]
D: [opcja 4]
Poprawna odpowiedź: [litera poprawnej opcji]

Nie generuj pytania podobnego do poniższych:
{existing_questions}
"""

generate_question_prompt = PromptTemplate.from_template(generate_question_template)

llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4")
generate_question_chain = LLMChain(llm=llm, prompt=generate_question_prompt)


def load_existing_questions():
    if os.path.exists("questions.txt"):
        with open("questions.txt", "r", encoding="utf-8") as file:
            return file.read()
    return ""


def save_question(question_text):
    with open("questions.txt", "a", encoding="utf-8") as file:
        file.write(question_text + "\n")


def clear_questions_file():
    if os.path.exists("questions.txt"):
        with open("questions.txt", "w", encoding="utf-8") as file:
            file.write("")


def generate_question(subject):
    existing_questions = load_existing_questions()
    response = generate_question_chain.run(subject=subject, existing_questions=existing_questions)
    save_question(response)
    return response


def parse_question(question_text):
    lines = question_text.strip().split('\n')
    if len(lines) != 6:
        return None, None, None
    question = lines[0].replace('Pytanie: ', '').strip()
    options = {
        'A': lines[1].replace('A: ', '').strip(),
        'B': lines[2].replace('B: ', '').strip(),
        'C': lines[3].replace('C: ', '').strip(),
        'D': lines[4].replace('D: ', '').strip()
    }
    correct_answer = lines[5].replace('Poprawna odpowiedź: ', '').strip()[0]
    return question, options, correct_answer

def main():
    st.title("Quiz")

    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.current_question = 0
        st.session_state.correct_answers_count = 0
        st.session_state.questions = []
        st.session_state.show_feedback = False
        st.session_state.feedback_message = ""
        st.session_state.subject_selected = False

    if not st.session_state.subject_selected:
        subjects = ['Matematyka', 'Fizyka', 'Informatyka', 'Chemia']
        selected_subject = st.selectbox("Wybierz dyscyplinę:", subjects)
    else:
        selected_subject = st.session_state.selected_subject

    if not st.session_state.quiz_started:
        if st.button("Rozpocznij quiz"):
            st.session_state.quiz_started = True
            st.session_state.subject_selected = True
            st.session_state.selected_subject = selected_subject
            st.session_state.current_question = 0
            st.session_state.correct_answers_count = 0
            st.session_state.questions = []
            st.session_state.show_feedback = False
            st.session_state.feedback_message = ""

            for _ in range(10):
                question_text = generate_question(selected_subject)
                question, options, correct_answer = parse_question(question_text)
                if question and options and correct_answer:
                    st.session_state.questions.append((question, options, correct_answer))

    if st.session_state.quiz_started:
        if st.session_state.current_question < 10:
            question, options, correct_answer = st.session_state.questions[st.session_state.current_question]
            st.write(f"\nPytanie {st.session_state.current_question + 1}:")
            st.write(question)
            if options:  # Add check to ensure options is not None
                user_answer = st.radio("Twoja odpowiedź:", list(options.keys()), format_func=lambda x: f"{x}: {options[x]}", index=None, key=f"question_{st.session_state.current_question}")

                if st.button("Sprawdź odpowiedź", key=f"check_{st.session_state.current_question}"):
                    if user_answer == correct_answer:
                        st.session_state.feedback_message = "Poprawna odpowiedź!"
                        st.session_state.correct_answers_count += 1
                    else:
                        st.session_state.feedback_message = f"Niepoprawna odpowiedź. Poprawna odpowiedź to {correct_answer}: {options[correct_answer]}."
                    st.session_state.show_feedback = True

                if st.session_state.show_feedback:
                    st.write(st.session_state.feedback_message)
                    if st.button("Następne pytanie", key=f"next_{st.session_state.current_question}"):
                        st.session_state.current_question += 1
                        st.session_state.show_feedback = False
                        if st.session_state.current_question == 10:
                            clear_questions_file()  # Clear the file after the last question
                        st.rerun()
        else:
            st.write(f"\nTwój wynik: {st.session_state.correct_answers_count} / 10")
            st.session_state.quiz_started = False
            st.session_state.subject_selected = False


if __name__ == "__main__":
    main()