import json
import streamlit as st
import requests

# Define the API endpoints
SUBMIT_DATA_API = "https://dev-appmod.techo.camp/compiler/generate_script"
UPDATE_DATA_API = "https://dev-appmod.techo.camp/compiler/create_compiler"
GET_CARDS_API = "https://dev-appmod.techo.camp/compiler/get_all_compilers"
TEST_API = "https://dev-appmod.techo.camp/compiler/run_cmd_on_compiler"


# Function to call API to submit data
def call_submit_data_api(data):
    data["files"] = []
    response = requests.request(
        "POST",
        SUBMIT_DATA_API,
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )
    return response.json()


# Function to call API to update data
def call_update_data_api(data, language):
    data["shell_script"] = data.pop("script")
    data["language"] = language
    response = requests.request(
        "POST",
        UPDATE_DATA_API,
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )
    return response.json()


# Function to call API to get cards
def call_get_cards_api():
    response = requests.request(
        "GET", GET_CARDS_API, headers={"Content-Type": "application/json"}
    )
    return response.json()


# Function to display the card in Step 3
def display_cards(cards):
    st.write("### Information Cards")
    for card in cards:
        with st.container():
            st.write("#### Card")
            with st.expander("Card Details", expanded=True):
                for key, value in card.items():
                    if key == "script":
                        # st.write(f"##### Resultant Shell Script:")
                        st.markdown(f"<span style='color: SlateBlue; font-weight: bold;'>{key.capitalize().replace('_', ' ')}:</span>", unsafe_allow_html=True)
                        st.code(value, language="bash")
                    else:
                        # st.write(f"**{key}:** {value}")
                        # st.write(f"##### {key}:")
                        st.markdown(f"<span style='color: SlateBlue; font-weight: bold;'>{key.capitalize().replace('_', ' ')}:</span>\n{value}", unsafe_allow_html=True)
            st.write("---")

            st.write("#### Test Command")
            col1, col2 = st.columns([3, 1])
            with col1:
                command_input = st.text_area(
                    "Enter Command",
                    key=f"command_{card['id']}",
                    placeholder="Type your command here...",
                )
            with col2:
                if st.button("Run Test Command", key=f"run_{card['id']}"):
                    payload = {
                        "compiler_name": card["vm_name"],
                        "command": st.session_state[f"command_{card['id']}"],
                        "task_id": "1234",
                    }
                    response = requests.request(
                        "POST",
                        TEST_API,
                        data=json.dumps(payload),
                        headers={"Content-Type": "application/json"},
                    )
                    with col1:
                        with st.expander("Test Command Output", expanded=True):
                            st.code(response.json().get("output", "No output received"), language="text")
            st.write("---")


# Main application logic
def main():
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Information Cards", "Multi-Step Form"])

    if selection == "Information Cards":
        cards = call_get_cards_api()
        display_cards(cards)

    if selection == "Multi-Step Form":
        st.title("Multi-Step Form")

        if "step" not in st.session_state:
            st.session_state.step = 1
        if "form_data" not in st.session_state:
            st.session_state.form_data = {}
        if "api_response" not in st.session_state:
            st.session_state.api_response = {}

        if st.session_state.step == 1:
            st.header("Step 1: Input Form and File Upload")

            with st.form(key="form1"):
                # st.session_state.form_data['language'] = st.text_input("Enter Programing Language:")
                st.session_state.form_data["language"] = st.text_input(
                    "Enter your Programing Language...",
                )
                st.session_state.form_data["Prompt"] = st.text_area(
                    "Describe Your Requirement for Compiler:"
                )
                submitted = st.form_submit_button("Next")

            if submitted:
                st.session_state.api_response = call_submit_data_api(
                    st.session_state.form_data
                )
                st.session_state.step = 2

        if st.session_state.step == 2:
            st.header("Step 2: Review and Edit Information")

            st.write("### API Response:")
            # st.code(st.session_state.api_response["script"], language="bash")

            # Provide an option for the user to update the shell script
            new_script = st.text_area("Edit Shell Script", st.session_state.api_response["script"], height=300)

            # Update the script in the session state if the user makes changes
            if new_script != st.session_state.api_response["script"]:
                st.session_state.api_response["script"] = new_script
                st.success("Script updated successfully!")

            st.write("---")
            st.write("### ID:")
            st.write(st.session_state.api_response["id"])

            if st.button("Submit"):
                st.session_state.api_response = call_update_data_api(
                    st.session_state.api_response,
                    st.session_state.form_data["language"],
                )
                st.session_state.step = 3

        if st.session_state.step == 3:
            st.header("Step 3: Information Cards")

            cards = call_get_cards_api()
            display_cards([cards[-1]])
            # print(cards[-1])


if __name__ == "__main__":
    main()