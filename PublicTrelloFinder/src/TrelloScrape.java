import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import org.jsoup.HttpStatusException;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class TrelloScrape
{
	private static final char[] chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ".toCharArray();

	private static Random rand = new Random();

	public static void main(String[] args) throws IOException
	{
		File file = new File("out.txt");
		FileWriter fr = new FileWriter(file, true);

		List<String> urls = new ArrayList<>();
		for(char c : chars)
		{
			boolean done = false;
			int start = 0;
			while(!done)
			{
				Document doc;
				try
				{
					String url = "https://www.google.com/search?q=" + c + "+site:trello.com/b/&start=" + start + "&rlz=1C1GCEA_enUS809US809&sxsrf=ACYBGNQ-mi3w77Qd8V-7BKq8LlaMeM5qCA:1580935076158&ei=pCc7XrmlCdS4tQas9pyQAg&sa=N&ved=2ahUKEwi5h4KNorvnAhVUXM0KHSw7ByIQ8tMDegQIZRAu&cshid=1580935087522478&biw=1064&bih=846";
					try
					{
						doc = Jsoup.connect(url).get();
					} catch(HttpStatusException ex)
					{
						if(ex.getStatusCode() == 429)
						{
							System.out.println("429!!!");
							done = true;
							return;
						}
						continue;
					}
					Elements results = doc.getElementsByClass("g");
					if(results.size() == 0)
					{
						done = true;
						continue;
					}
					start += results.size();
					for(Element element : results)
					{
						Element result = element.getElementsByClass("r").first();
						String link = result.getElementsByTag("a").first().attr("href");
						String name = result.getElementsByTag("a").first().getElementsByTag("h3").first().html();
						if(!urls.contains(link))
						{
							urls.add(link);
							fr.write(name + "  " + link + "\n");
							fr.flush();
						}
					}
					Thread.sleep(rand.nextInt(3000) + 3000);
				} catch(Exception e)
				{
					e.printStackTrace();
				}
			}
		}

		fr.close();
	}
}
