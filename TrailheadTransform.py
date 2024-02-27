import re
import argparse

def transform_question_block(block):
    lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
    question = lines[0]
    answers = []
    correct_answer_marker = "*"
    
    for line in lines[1:]:
        if 'Correct.' in line:
            answer_text = re.sub(r'^[A-D]\.\s*', '', line.split('Correct.')[0].strip())
            answers.append(f'{correct_answer_marker}{answer_text}')
        else:
            answer_text = re.sub(r'^[A-D]\.\s*', '', line)
            if '.' in answer_text:
                answer_text = answer_text.split('.')[0].strip()
            answers.append(answer_text)
    
    return '\n'.join([question] + answers)

def transform_file(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    question_blocks = re.split(r'Question \d+ of \d+', content)
    question_blocks = question_blocks[1:]
    
    transformed_content = [transform_question_block(block) for block in question_blocks]
    
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write('\n\n'.join(transformed_content))

def main():
    parser = argparse.ArgumentParser(description='Transforms a quiz source text into a specific format.')
    parser.add_argument('input_file', help='Path to the source text file.')
    parser.add_argument('output_file', help='Path to the output text file.')
    
    args = parser.parse_args()
    
    transform_file(args.input_file, args.output_file)
    
    print(f'Transformation complete. Output saved to {args.output_file}')

if __name__ == '__main__':
    main()
