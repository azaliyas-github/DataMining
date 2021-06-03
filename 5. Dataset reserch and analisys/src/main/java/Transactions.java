import au.com.bytecode.opencsv.*;
import lombok.*;

import java.io.*;
import java.util.*;

@Getter
public class Transactions {
	HashMap<Integer, ArrayList<Item>> transactions;


	public HashMap<Integer, ArrayList<Item>> getTransactionsArray(CSVReader csvReader) throws IOException {
		HashMap<Integer, ArrayList<Item>> allTransactions = new HashMap<>();
		String[] nextLine;
		int transactionNumber;
		String stokeCode;
		String description;
		int quantity;

		while ((nextLine = csvReader.readNext()) != null) {
			if (nextLine != null) {

				transactionNumber = Integer.parseInt(nextLine[1]);
				stokeCode = nextLine[2];
				description = nextLine[3];
				quantity = Integer.parseInt(nextLine[4]);

				if (allTransactions.containsKey(transactionNumber)) {
					allTransactions.get(transactionNumber).add(Item
						.builder()
						.stokeCode(stokeCode)
						.description(description)
						.quantity(quantity)
						.build());
				}
				else {
					ArrayList<Item> items = new ArrayList<>();
					items.add(Item
						.builder()
						.stokeCode(stokeCode)
						.description(description)
						.quantity(quantity)
						.build()
					);

					allTransactions.put(transactionNumber, items);
				}

			}
		}
		return allTransactions;
	}
}
