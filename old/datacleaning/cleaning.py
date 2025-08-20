import os

def remove_command_substrings(folder_path):
    """
    Remove specific command substrings from all .txt files without removing entire lines.
    """
    
    # Define the substrings to remove
    substrings_to_remove = [
        "Command: ON7",
        "Command: ON8", 
        "Command: OFF8",
        "Command: OFF7"
    ]
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    # Get all .txt files in the folder
    txt_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.txt')]
    
    if not txt_files:
        print(f"No .txt files found in '{folder_path}'")
        return
    
    print(f"Found {len(txt_files)} .txt files to process...")
    print(f"Removing substrings: {', '.join(substrings_to_remove)}")
    print()
    
    for filename in txt_files:
        file_path = os.path.join(folder_path, filename)
        
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Keep track of original content for comparison
            original_content = content
            
            # Remove each substring
            for substring in substrings_to_remove:
                content = content.replace(substring, "")
            
            # Check if any changes were made
            if original_content != content:
                # Write the modified content back to the file
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                # Count how many substrings were removed
                removals = []
                for substring in substrings_to_remove:
                    count = original_content.count(substring)
                    if count > 0:
                        removals.append(f"{substring} ({count}x)")
                
                print(f"✓ Processed: {filename}")
                print(f"  - Removed: {', '.join(removals)}")
            else:
                print(f"- No command substrings found: {filename}")
                
        except Exception as e:
            print(f"✗ Error processing {filename}: {str(e)}")

# Main execution
if __name__ == "__main__":
    # You can either input the path or hardcode it here
    folder_path = input("Enter the folder path containing .txt files: ").strip()
    
    # Remove quotes if user added them
    folder_path = folder_path.strip('"\'')
    
    # Alternative: hardcode your path here instead of input
    # folder_path = "/path/to/your/folder"
    
    # Process the files
    remove_command_substrings(folder_path)
    
    print("\nProcessing complete!")