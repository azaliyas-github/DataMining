import org.javatuples.*;

import java.util.*;

public class MultiStageAlgorithImpl {
	Transactions transactions;

	MultiStageAlgorithImpl(Transactions transactions) {
		this.transactions = transactions;
	}

	public Collection<String[]> getFrequentItems(int support) {

		//массив для синглтонов
		HashMap<String, Integer> singleItemFrequensy = new HashMap<>();
		// массивы для даблтонов
		HashMap<Integer, Integer> firstDoubleItemFrequensy = new HashMap<>();
		HashMap<Integer, Integer> secondDoubleItemFrequensy = new HashMap<>();

		for (var transaction : transactions.getTransactions().entrySet()) {
			for (var item : transaction.getValue()) {
				var stokeCode = item.getStokeCode();
				var newItemCount = singleItemFrequensy.getOrDefault(stokeCode, 0) + 1;
				singleItemFrequensy.put(stokeCode, newItemCount);
			}
		}

		for (var transaction : transactions.getTransactions().entrySet()) {
			var itemsCount = transaction.getValue().size();
			for (var i = 0; i < itemsCount; ++i) {
				for (var j = i + 1; j < itemsCount; ++j) {
					var firstStokeCode = transaction.getValue().get(i).getStokeCode();
					var secondStokeCode = transaction.getValue().get(j).getStokeCode();

					var firstHash = (firstStokeCode.hashCode() + secondStokeCode.hashCode()) % singleItemFrequensy.size();
					var newItemCount = firstDoubleItemFrequensy.getOrDefault(firstHash, 0) + 1;
					firstDoubleItemFrequensy.put(firstHash, newItemCount);

					var secondHash = (firstStokeCode.hashCode() + secondStokeCode.hashCode() * 2) % singleItemFrequensy.size();
					newItemCount = secondDoubleItemFrequensy.getOrDefault(secondHash, 0) + 1;
					secondDoubleItemFrequensy.put(secondHash, newItemCount);
				}
			}
		}
		HashMap<Pair<String, String>, Integer> doubleItemFrequensy = new HashMap<>();
		for (var transaction : transactions.getTransactions().values()) {
			var itemsCount = transaction.size();
			for (var i = 0; i < itemsCount; ++i) {
				for (var j = i + 1; j < itemsCount; ++j) {
					var firstStokeCode = transaction.get(i).getStokeCode();
					var secondStokeCode = transaction.get(j).getStokeCode();

					var firstHash = (firstStokeCode.hashCode() + secondStokeCode.hashCode())
						% singleItemFrequensy.size();
					var secondHash = (firstStokeCode.hashCode() + secondStokeCode.hashCode() * 2)
						% singleItemFrequensy.size();

					if (singleItemFrequensy.get(firstStokeCode) >= support
						&& singleItemFrequensy.get(secondStokeCode) >= support
						&& firstDoubleItemFrequensy.get(firstHash) >= support
						&& secondDoubleItemFrequensy.get(secondHash) >= support) {

						Pair<String, String> pair = new Pair<>(firstStokeCode, secondStokeCode);
						var newItemCount = doubleItemFrequensy.getOrDefault(pair, 0) + 1;
						doubleItemFrequensy.put(pair, newItemCount);
					}
				}
			}
		}

		Collection<String[]> frequentItemSets = new ArrayList<>();
		for (Map.Entry<String, Integer> item : singleItemFrequensy.entrySet()) {
			if (item.getValue() >= support)
				frequentItemSets.add(new String[]{item.getKey()});
		}

		for (Map.Entry<Pair<String, String>, Integer> item : doubleItemFrequensy.entrySet()) {
			if (item.getValue() >= support)
				frequentItemSets.add(new String[] {
					item.getKey().getValue0(),
					item.getKey().getValue1()});
		}
		return frequentItemSets;
	}
}
