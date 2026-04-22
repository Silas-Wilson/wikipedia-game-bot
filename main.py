import scraper
import embedder
import os

BATCH_SIZE = 50

def batch_array(array, batch_size):
    return [array[i:i + batch_size] for i in range(0, len(array), batch_size)]

def get_best_matching_hyperlink(current_url, target_url, target_embedding_paragraph = None, url_history = None):
    print("Current URL: " + current_url)

    #Initialize target embedding and URL history
    if target_embedding_paragraph is None:
        target_first_paragraph = scraper.get_first_n_paragraphs(target_url, 1)
        target_embedding_paragraph = embedder.get_embeddings([target_first_paragraph])[0]
    if url_history is None:
        url_history = []

    url_history.append(current_url)

    #Acquire and batch all hyperlink URLs
    urls_on_page = scraper.get_all_hyperlink_urls(current_url)
    urls_on_page_batched = batch_array(urls_on_page, BATCH_SIZE)

    #Check if the target link is on this page
    if target_url in urls_on_page:
        url_history.append(target_url)
        print("Current URL: " + target_url)
        print("Target URL found!")
        return url_history

    #Acquire hyperlink URL page title embeddings
    urls_on_page_embeddings = []
    for batch in urls_on_page_batched:
        batch_titles = [scraper.get_page_title(url) for url in batch]
        batch_embeddings = embedder.get_embeddings(batch_titles)
        urls_on_page_embeddings.extend(batch_embeddings)

    #Determine most similar URL to target URL
    most_similar_url = url_history[-2] if len(url_history) >= 2 else "EPIC FAIL!y"
    highest_similarity = -1
    for embedding, url in zip(urls_on_page_embeddings, urls_on_page):
        similarity_to_target = embedder.cosine_similarity(embedding, target_embedding_paragraph)

        if (url not in url_history) and (similarity_to_target > highest_similarity):
            most_similar_url = url
            highest_similarity = similarity_to_target

    return get_best_matching_hyperlink(most_similar_url, target_url, target_embedding_paragraph, url_history)

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    #Get first URL
    have_first_url = False
    while not have_first_url:
        clear_terminal()

        starting_query = input("Type the name of the starting Wikipedia page: ")
        starting_link = scraper.search_wikipedia(starting_query + " ")

        clear_terminal()

        if starting_link == None:
            print("No pages found!")
            input("Press ENTER to continue")
            continue
       
        print("This is the page I found: " + starting_link)
        answer = input("Does this look correct? (Y/N): ").strip()

        if answer.upper() == "Y":
            have_first_url = True
            
    #Get second URL
    have_second_url = False
    while not have_second_url:
        clear_terminal()

        target_query = input("Type the name of the target Wikipedia page: ")
        target_link = scraper.search_wikipedia(target_query)

        clear_terminal()

        if target_link == None:
            print("No pages found!")
            input("Press ENTER to continue")
            continue
       
        print("This is the page I found: " + target_link)
        answer = input("Does this look correct? (Y/N): ").strip()

        if answer.upper() == "Y":
            have_second_url = True

    clear_terminal()
    path = get_best_matching_hyperlink(starting_link, target_link)

    print(f"\nI went from {scraper.get_page_title(starting_link)} to {scraper.get_page_title(target_link)} in {len(path) - 1} clicks!")

    path_string = ""
    for url in path:
        title = scraper.get_page_title(url)
        path_string += title + " -> "
    print(path_string[:-4])

    play_again = input("\nWould you like to try again? (Y/N): ")

    if play_again.upper() == "Y": main()

main()