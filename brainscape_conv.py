import sys

def parse_source_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    questions = []
    answers = []
    correct_answers = set()
    parsing_correct_answers = False
    skip_next_line = False  # Flag to skip the question number line
    question_text = ""
    
    for line in lines:
        if line.startswith('--'):
            skip_next_line = True  # Next line will be the question number, skip it
            if question_text:  # If there's a question to be added
                questions.append((question_text, answers, correct_answers))
                answers = []
                correct_answers = set()
            parsing_correct_answers = False
        elif skip_next_line:
            skip_next_line = False  # Skip the current line (question number)
            continue
        elif line.strip() == 'Q':
            question_text = ""
        elif line.startswith('A') and len(line.strip()) == 1:
            parsing_correct_answers = True
        elif parsing_correct_answers:
            correct_answers.add(line.strip()[3:])  # Remove the answer letter prefix
        elif line.strip():
            if not question_text:
                question_text = line.strip()
            else:
                answers.append(line.strip()[3:])  # Remove the answer letter prefix
                
    # Add the last question if any
    if question_text:
        questions.append((question_text, answers, correct_answers))
    
    return questions

def write_target_file(questions, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for question, answers, correct_answers in questions:
            file.write(question + "\n")
            for answer in answers:
                if answer in correct_answers:
                    file.write("*" + answer + "\n")
                else:
                    file.write(answer + "\n")
            file.write("\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <source_file_path> <target_file_path>")
        sys.exit(1)

    source_file_path = sys.argv[1]
    target_file_path = sys.argv[2]
    questions = parse_source_file(source_file_path)
    write_target_file(questions, target_file_path)
    print(f"Conversion completed successfully. Output saved to {target_file_path}")
