import java.util.ArrayList;
import java.util.List;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class TrelloScrape {
	private static final char[] chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".toCharArray();

	public static void main(String[] args) {
		List<String> urls = new ArrayList<>();
		int start = 0;
		for (char c : chars) {
			boolean done = false;
			start = 0;
			while (!done) {
				Document doc;
				try {

					String url = "https://www.google.com/search?q=" + String.valueOf(c) + "+site:trello.com/b/&start="
							+ start;
					doc = Jsoup.connect(url).get();
					Elements results = doc.getElementsByClass("g");
					if (results.size() == 0) {
						done = true;
						continue;
					}
					start += results.size();
					for (int i = 0; i < results.size(); i++) {
						Element result = results.get(i).getElementsByClass("r").first();
						String link = result.getElementsByTag("a").first().attr("href");
						String name = result.getElementsByTag("a").first().getElementsByTag("h3").first().html();
						if (!urls.contains(link)) {
							urls.add(link);
							System.out.println(name + "  " + link);
						}
					}
				} catch (Exception e) {
					e.printStackTrace();
					continue;
				}
			}
		}
	}
}
