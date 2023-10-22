import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import base64


DATA_FILE = "stress_data.csv"
def clear_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
def save_data(date, total_stress, journal_entry):
    if os.path.exists(DATA_FILE):
        data = pd.read_csv(DATA_FILE)
    else:
        data = pd.DataFrame(columns=["Date", "Stress Level", "Journal"])
    
    new_data = pd.DataFrame([{"Date": date, "Stress Level": total_stress, "Journal": journal_entry}])
    data = pd.concat([data, new_data], ignore_index=True)
    data.to_csv(DATA_FILE, index=False)

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Date", "Stress Level", "Journal"])

def create_download_link_for_binary(filename, download_name):
    with open(filename, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{download_name}">Download PDF</a>'

def main():
    st.image("EmployEase-01.png", use_column_width=True)
    st.title("Daily Stress Level Measurement")
    if "initialized" not in st.session_state:
        clear_data()
        st.session_state.initialized = True
    st.sidebar.header("Options")
    display_history = st.sidebar.checkbox("Display Stress Level History", False)

    date = st.date_input("Select the date for check-in", pd.Timestamp.today() - pd.Timedelta(days=17))

    # Check if date has changed and reset
    if "prev_date" not in st.session_state:
        st.session_state.prev_date = date
    elif st.session_state.prev_date != date:
        st.session_state.prev_date = date
        st.experimental_rerun()

    if display_history:
        data = load_data()
        if not data.empty:
            st.subheader("Your Stress Level History")
            fig, ax = plt.subplots()
            ax.plot(data["Date"], data["Stress Level"], marker='o', linestyle='-', color='black')
            
            # Labels and styling
            ax.set_facecolor('white')
            ax.grid(color='black', linestyle='-', linewidth=0.5)
            ax.set_xlabel('Date', color='white')
            ax.set_ylabel('Stress Level', color='white')
            ax.set_xticklabels(data["Date"], rotation=45, ha="right", color='black')
            ax.tick_params(axis='both', colors='black')
            ax.set_title('Your Stress Levels Over Time', color='black')
            
            st.pyplot(fig)

            # Save the figure to PDF and provide a download link
            pdf_filename = "stress_level_history.pdf"
            fig.savefig(pdf_filename, bbox_inches='tight')
            st.markdown(create_download_link_for_binary(pdf_filename, pdf_filename), unsafe_allow_html=True)

            # Display journal entries
            for _, row in data.iterrows():
                if pd.notna(row["Journal"]):  # Skip NaN values
                    st.subheader(f"Journal Entry for {row['Date']}:")
                    st.write(row["Journal"])
        else:
            st.write("No history found.")
    else:
        # Questions
        questions = [
            "Do you often feel overwhelmed?",
            "Do you struggle to sleep because of stress?",
            "Do you find it hard to concentrate?",
            "Do you feel constantly tired?",
            "Do you get headaches or migraines often?"
        ]

        default_values = [5] * len(questions)

        # Collect answers
        answers = []
        for q, default in zip(questions, default_values):
            ans = st.slider(q, 0, 10, int(default))
            answers.append(ans)

        total_stress = sum(answers)
        st.subheader(f"Your Stress Level for {date}: {total_stress} / {len(questions) * 10}")

        # Journal entry
        journal_entry = st.text_area("Journal Entry", "")

        # Save data
        if st.button("Save"):
            save_data(date, total_stress, journal_entry)
            st.success("Saved successfully!")

if __name__ == "__main__":
    main()
