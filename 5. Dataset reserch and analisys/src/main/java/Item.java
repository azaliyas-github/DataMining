import lombok.*;

@Data
@Builder
public class Item {
	private String stokeCode;
	private String description;
	private int quantity;
}
