from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import streamlit as st


openai_api_key = ''


generate_question_template = """
Wygeneruj unikalne pytanie quizowe dla {subject} z czterema możliwymi odpowiedziami, gdzie tylko jedna odpowiedź jest poprawna. Podaj poprawną odpowiedź oraz trzy niepoprawne odpowiedzi.
Sformatuj odpowiedź w następujący sposób:
Pytanie: [treść pytania]
A: [opcja 1]
B: [opcja 2]
C: [opcja 3]
D: [opcja 4]
Poprawna odpowiedź: [litera poprawnej opcji]
"""

generate_question_prompt = PromptTemplate.from_template(generate_question_template)

llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-3.5-turbo")
generate_question_chain = LLMChain(llm=llm, prompt=generate_question_prompt)


def generate_question(subject):
    response = generate_question_chain.run(subject=subject)
    return response


def parse_question(question_text):
    lines = question_text.strip().split('\n')
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

    subjects = ['Matematyka', 'Fizyka', 'Informatyka', 'Chemia']
    selected_subject = st.selectbox("Wybierz dyscyplinę:", subjects)

    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.current_question = 0
        st.session_state.correct_answers_count = 0
        st.session_state.questions = []
        st.session_state.show_feedback = False
        st.session_state.feedback_message = ""

    if st.button("Rozpocznij quiz") or st.session_state.quiz_started:
        if not st.session_state.quiz_started:
            st.session_state.quiz_started = True
            st.session_state.current_question = 0
            st.session_state.correct_answers_count = 0
            st.session_state.questions = []
            st.session_state.show_feedback = False
            st.session_state.feedback_message = ""
            for _ in range(10):
                question_text = generate_question(selected_subject)
                question, options, correct_answer = parse_question(question_text)
                st.session_state.questions.append((question, options, correct_answer))

        if st.session_state.current_question < 10:
            question, options, correct_answer = st.session_state.questions[st.session_state.current_question]
            st.write(f"\nPytanie {st.session_state.current_question + 1}:")
            st.write(question)
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
                    st.rerun()
        else:
            st.write(f"\nTwój wynik: {st.session_state.correct_answers_count} / 10")
            st.session_state.quiz_started = False


if __name__ == "__main__":
    main()
