import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class TrelloScrape {
	public static void main(String[] args) {
		int start = 0;
		while (true) {
			Document doc;
			try {
				doc = Jsoup.connect("https://www.google.com/search?q=site:trello.com/b/&start=" + start).get();
				Elements results = doc.getElementsByClass("g");
				start += results.size();
				for (int i = 0; i < results.size(); i++) {
					Element result = results.get(i).getElementsByClass("r").first();
					String link = result.getElementsByTag("a").first().attr("href");
					String name = result.getElementsByTag("a").first().getElementsByTag("h3").first().html();
					System.out.println(name + "  " + link);
				}
			} catch (Exception e) {
				continue;
			}
		}
	}
}
