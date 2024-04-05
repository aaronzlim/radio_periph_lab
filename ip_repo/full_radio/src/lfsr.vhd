----------------------------------------------------------------------------------
-- Aaron Lim
-- 13 MAR 2024
--
-- Linear feedback shift register for pseudo random number generation.
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity LFSR is
-- generic ();
port (
   I_CLK  : in  std_logic;
   I_RSTN : in  std_logic;
   I_SYNC : in  std_logic := '0';
   I_SEED : in  std_logic_vector(31 downto 0) := (others => '0');
   I_EN   : in  std_logic := '1';
   O_DATA : out std_logic_vector(31 downto 0)
);
end LFSR;

architecture LFSR_ARCH of LFSR is

   constant C_ORDER    : positive                             := 32;
   constant C_POLY     : unsigned(C_ORDER-1 downto 0)         := x"B4BCD35C";

   -- SIGNALS --
   
   signal lfsr : std_logic_vector(C_ORDER downto 1);
   signal mask : std_logic_vector(C_ORDER downto 1);
   signal poly : std_logic_vector(C_ORDER downto 1);

begin

   poly <= std_logic_vector(C_POLY);
   mask_gen : for k in C_ORDER downto 1 generate
      mask(k) <= poly(k) and lfsr(1);
   end generate mask_gen;
   
   lfsr_proc : process (I_CLK)
   begin
      if rising_edge(I_CLK) then
         if I_EN = '1' then
            lfsr <= '0' & lfsr(C_ORDER downto 2) xor mask;
         end if;
         
         if I_SYNC = '1' then
            lfsr <= I_SEED;
         end if;
         
         if I_RSTN = '0' then
            lfsr <= (others => '1');
         end if;
      end if;
   end process lfsr_proc;
   
   O_DATA <= lfsr(C_ORDER downto 1);

end LFSR_ARCH;
