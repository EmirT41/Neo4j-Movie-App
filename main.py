from database_process import Database_Connection, Movie_Repository
from movie import Movie
import os, time

def main():
    try:
        print("Bağlantı kuruluyor...")
        conn = Database_Connection("bolt://localhost:7687", "neo4j", "şifreniz")
        os.system("cls")
    except RuntimeError as e:
        os.system("cls")
        print(e)
        return
    
    repo = Movie_Repository(conn)
    movie_app = Movie(repo)
    current_results = []

    while True:
        print("\n--- MENU ---")
        print("1. Film Ara")
        print("2. Film Detayı Göster")
        print("3. Seçili Film için graph.json Oluştur")
        print("4. Çıkış")
        
        choice = input("Seçiminiz: ")

        if choice == "1":
            keyword = input("Aranacak film adı: ")
            os.system("cls")
            try:
                current_results = movie_app.search_and_list(keyword)
            except RuntimeError as e:
                os.system("cls")
                print(e)
                return

        elif choice == "2":
            if not current_results:
                os.system("cls")
                print("Lütfen önce (1) ile arama yapın.")
                time.sleep(1.5)
                os.system("cls")
                continue
            try:
                idx = int(input("Film numarası seçin: ")) - 1
                if 0 <= idx < len(current_results):
                    movie_app.show_details(current_results[idx]['title'])
                else:
                    os.system("cls")
                    print(f"Hatalı numara! {idx}")
                    time.sleep(1.5)
                    os.system("cls")
            except RuntimeError as e:
                os.system("cls")
                print(e)
                return

            except ValueError:
                os.system("cls")
                print("Lütfen geçerli bir sayı girin.")
                time.sleep(1.5)
                os.system("cls")

        elif choice == "3":
            try:
                movie_app.export_to_json()
            except RuntimeError as e:
                os.system("cls")
                print(e)
                return

        elif choice == "4":
            os.system("cls")
            print("Programdan çıkılıyor...")
            break
        else:
            os.system("cls")
            print(f"Geçersiz seçim! {choice}")
            time.sleep(1.5)
            os.system("cls")

    conn.close()

if __name__ == "__main__":
    main()